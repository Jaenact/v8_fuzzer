from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
from pathlib import Path

from fuzzer.corpus import Corpus
from fuzzer.generator import generate_program
from fuzzer.mutators import MutatorPool, splice_programs
from fuzzer.runner import D8Runner, differential_interesting
from fuzzer.reducer import minimize_by_lines


def resolve_binary(path_or_name: str) -> str:
    resolved = shutil.which(path_or_name)
    if resolved:
        return resolved
    p = Path(path_or_name)
    if p.exists() and p.is_file():
        return str(p)
    raise FileNotFoundError(f"d8 binary not found: {path_or_name}")


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
    parser.add_argument("--minimize-crashes", action="store_true")
    parser.add_argument("--import-seeds-dir", help="Directory with *.js seeds to import before fuzzing")
    parser.add_argument("--import-seeds-limit", type=int, default=1000)
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

    imported = 0
    if args.import_seeds_dir:
        imported = queue.import_directory(Path(args.import_seeds_dir), limit=args.import_seeds_limit)

    primary = D8Runner(resolve_binary(args.d8_path), timeout_sec=args.timeout, flags=parse_flags(args.primary_flags))
    secondary = None
    if args.secondary_d8_path:
        secondary = D8Runner(
            resolve_binary(args.secondary_d8_path),
            timeout_sec=args.timeout,
            flags=parse_flags(args.secondary_flags),
        )

    mutators = MutatorPool()
    seen_fingerprints: set[str] = set()
    unique_crashes: set[str] = set()
    counters = {
        "iterations": 0,
        "corpus_add": 0,
        "imported_seeds": imported,
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
            stable = hashlib.sha256(f"{result.returncode}:{result.stderr[:400]}".encode("utf-8", errors="ignore")).hexdigest()
            crash_fp = f"{result.returncode}:{stable[:16]}"
            out = crashes / f"crash_{i:06d}_{result.returncode}.js"
            out.write_text(program, encoding="utf-8")
            if args.minimize_crashes:

                def _repro(src: str) -> bool:
                    tmp_min = tmp / f"min_repro_{i:06d}.js"
                    tmp_min.write_text(src, encoding="utf-8")
                    rr = primary.run(tmp_min)
                    return rr.crashed

                minimized = minimize_by_lines(program, _repro)
                (crashes / f"crash_{i:06d}_{result.returncode}.min.js").write_text(minimized, encoding="utf-8")
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
            if queue.add(program):
                counters["corpus_add"] += 1
            queue.mark_novel(seed_name)
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
            payload = {**counters, "mutators": mutators.stats()}
            stats.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(
                f"[*] iter={i+1}, corpus={len(queue.seeds())}, uniq={len(seen_fingerprints)}, "
                f"crash={counters['crashes']}, diff={counters['differentials']}"
            )

    stats.write_text(json.dumps({**counters, "mutators": mutators.stats()}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
