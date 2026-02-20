from __future__ import annotations

import random
from pathlib import Path


class Corpus:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def seeds(self) -> list[Path]:
        return sorted(self.root.glob("*.js"))

    def choose_seed(self, rng: random.Random) -> str | None:
        seeds = self.seeds()
        if not seeds:
            return None
        return rng.choice(seeds).read_text(encoding="utf-8")

    def add(self, program: str) -> Path:
        next_id = len(self.seeds())
        out = self.root / f"seed_{next_id:06d}.js"
        out.write_text(program, encoding="utf-8")
        return out


def mutate_text(base: str, rng: random.Random) -> str:
    lines = [ln for ln in base.splitlines() if ln.strip()]
    if not lines:
        return base

    choice = rng.randint(0, 2)
    if choice == 0:
        insert_at = rng.randint(0, len(lines))
        lines.insert(insert_at, f"let _f{rng.randint(0, 9999)} = {rng.randint(-999999,999999)};")
    elif choice == 1 and len(lines) >= 2:
        i = rng.randint(0, len(lines) - 1)
        j = rng.randint(0, len(lines) - 1)
        lines[i], lines[j] = lines[j], lines[i]
    else:
        i = rng.randint(0, len(lines) - 1)
        lines[i] = lines[i].replace("0", str(rng.randint(1, 9)), 1)

    return "\n".join(lines) + "\n"
