from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from fuzzer.corpus import Corpus
from fuzzer.generator import generate_program
from fuzzer.mutators import MutatorPool, splice_programs
from fuzzer.runner import D8Runner, differential_interesting


def parse_flags(raw: str) -> list[str]:
    return [x for x in raw.split() if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-oriented V8 fuzzer")
    parser.add_argument("--d8-path", required=True, help="Path to primary d8 binary")
    parser.add_argument("--secondary-d8-path", help="Optional secondary d8 for differential fuzzing")
    parser.add_argument("--primary-flags", default="")
    parser.add_argument("--secondary-flags", default="")
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--workdir", default=".fuzz-work")
    parser.add_argument("--generate-ratio", type=float, default=0.25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    workdir = Path(args.workdir)
    queue = Corpus(workdir / "corpus")
    crashes = workdir / "crashes"
    diffs = workdir / "differentials"
    tmp = workdir / "tmp"
    stats = workdir / "stats.json"
    crashes.mkdir(parents=True, exist_ok=True)
    diffs.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)

    primary = D8Runner(args.d8_path, timeout_sec=args.timeout, flags=parse_flags(args.primary_flags))
    secondary = None
    if args.secondary_d8_path:
        secondary = D8Runner(
            args.secondary_d8_path,
            timeout_sec=args.timeout,
            flags=parse_flags(args.secondary_flags),
        )

    mutators = MutatorPool()
    seen_fingerprints: set[str] = set()
    unique_crashes: set[str] = set()
    counters = {
        "iterations": 0,
        "corpus_add": 0,
        "crashes": 0,
        "unique_crashes": 0,
        "differentials": 0,
    }

    for i in range(args.iterations):
        base, seed_name = queue.choose_seed(rng)

        if base is None or rng.random() < args.generate_ratio:
            program = generate_program(rng)
            mutator_name = "generator"
        else:
            if rng.random() < 0.15:
                other, _ = queue.choose_seed(rng)
                program = splice_programs(base, other or generate_program(rng), rng)
                mutator_name = "splice"
            else:
                m = mutators.choose(rng)
                program = m.fn(base, rng)
                mutator_name = m.name

        sample_path = tmp / f"sample_{i:06d}.js"
        sample_path.write_text(program, encoding="utf-8")

        result = primary.run(sample_path)
        fp = result.fingerprint

        delta = 0.0
        if result.crashed:
            crash_fp = f"{result.returncode}:{hash(result.stderr[:400])}"
            out = crashes / f"crash_{i:06d}_{result.returncode}.js"
            out.write_text(program, encoding="utf-8")
            (crashes / f"crash_{i:06d}_{result.returncode}.log").write_text(
                f"cmd={' '.join(result.cmdline)}\nreturncode={result.returncode}\n\nSTDERR\n{result.stderr}\n\nSTDOUT\n{result.stdout}\n",
                encoding="utf-8",
            )
            counters["crashes"] += 1
            queue.mark_crash(seed_name)
            delta += 5.0
            if crash_fp not in unique_crashes:
                unique_crashes.add(crash_fp)
                counters["unique_crashes"] += 1
        elif (not result.timed_out) and (fp not in seen_fingerprints):
            seen_fingerprints.add(fp)
            queue.add(program)
            queue.mark_novel(seed_name)
            counters["corpus_add"] += 1
            delta += 1.5

        if secondary:
            sec = secondary.run(sample_path)
            if differential_interesting(result, sec):
                counters["differentials"] += 1
                delta += 3.0
                case_id = f"diff_{i:06d}"
                (diffs / f"{case_id}.js").write_text(program, encoding="utf-8")
                (diffs / f"{case_id}.json").write_text(
                    json.dumps(
                        {
                            "primary": {
                                "cmd": result.cmdline,
                                "returncode": result.returncode,
                                "timed_out": result.timed_out,
                                "stdout": result.stdout[:2000],
                                "stderr": result.stderr[:2000],
                            },
                            "secondary": {
                                "cmd": sec.cmdline,
                                "returncode": sec.returncode,
                                "timed_out": sec.timed_out,
                                "stdout": sec.stdout[:2000],
                                "stderr": sec.stderr[:2000],
                            },
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

        mutators.reward(mutator_name, delta)

        counters["iterations"] = i + 1
        if (i + 1) % 100 == 0:
            stats.write_text(json.dumps(counters, indent=2), encoding="utf-8")
            print(
                f"[*] iter={i+1}, corpus={len(queue.seeds())}, uniq={len(seen_fingerprints)}, "
                f"crash={counters['crashes']}, diff={counters['differentials']}"
            )

    stats.write_text(json.dumps(counters, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
