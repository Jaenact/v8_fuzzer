from __future__ import annotations

import argparse
import random
from pathlib import Path

from fuzzer.corpus import Corpus, mutate_text
from fuzzer.generator import generate_program
from fuzzer.runner import D8Runner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-oriented V8 fuzzer MVP")
    parser.add_argument("--d8-path", required=True, help="Path to d8 binary")
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--workdir", default=".fuzz-work")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    workdir = Path(args.workdir)
    queue = Corpus(workdir / "corpus")
    crashes = workdir / "crashes"
    tmp = workdir / "tmp"
    crashes.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)

    runner = D8Runner(args.d8_path, timeout_sec=args.timeout)
    seen_fingerprints: set[str] = set()

    for i in range(args.iterations):
        base = queue.choose_seed(rng)
        if base is None or rng.random() < 0.4:
            program = generate_program(rng)
        else:
            program = mutate_text(base, rng)

        sample_path = tmp / f"sample_{i:06d}.js"
        sample_path.write_text(program, encoding="utf-8")

        result = runner.run(sample_path)
        fp = result.fingerprint

        if result.crashed:
            out = crashes / f"crash_{i:06d}_{result.returncode}.js"
            out.write_text(program, encoding="utf-8")
            print(f"[!] crash saved: {out}")
            (crashes / f"crash_{i:06d}_{result.returncode}.log").write_text(
                f"returncode={result.returncode}\n\nSTDERR\n{result.stderr}\n\nSTDOUT\n{result.stdout}\n",
                encoding="utf-8",
            )
        elif (not result.timed_out) and (fp not in seen_fingerprints):
            seen_fingerprints.add(fp)
            queue.add(program)

        if (i + 1) % 100 == 0:
            print(f"[*] iter={i+1}, corpus={len(queue.seeds())}, unique={len(seen_fingerprints)}")


if __name__ == "__main__":
    main()
