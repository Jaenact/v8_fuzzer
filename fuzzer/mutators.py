from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

MutatorFn = Callable[[str, random.Random], str]


def _nonempty_lines(src: str) -> list[str]:
    return [ln for ln in src.splitlines() if ln.strip()]


def insert_statement(src: str, rng: random.Random) -> str:
    lines = _nonempty_lines(src)
    if not lines:
        return src
    idx = rng.randint(0, len(lines))
    lines.insert(idx, f"let __m{rng.randint(0,9999)} = ({rng.randint(-2**20,2**20)} ^ {rng.randint(0,2**16)});")
    return "\n".join(lines) + "\n"


def duplicate_block(src: str, rng: random.Random) -> str:
    lines = _nonempty_lines(src)
    if len(lines) < 3:
        return insert_statement(src, rng)
    start = rng.randint(0, len(lines) - 2)
    end = min(len(lines), start + rng.randint(1, 4))
    insert_at = rng.randint(0, len(lines))
    block = lines[start:end]
    lines[insert_at:insert_at] = block
    return "\n".join(lines) + "\n"


def tweak_numeric_literal(src: str, rng: random.Random) -> str:
    lines = _nonempty_lines(src)
    if not lines:
        return src
    line_i = rng.randint(0, len(lines) - 1)
    line = lines[line_i]
    digits = [i for i, c in enumerate(line) if c.isdigit()]
    if not digits:
        return insert_statement(src, rng)
    pos = rng.choice(digits)
    lines[line_i] = line[:pos] + str(rng.randint(0, 9)) + line[pos + 1 :]
    return "\n".join(lines) + "\n"


def splice_programs(a: str, b: str, rng: random.Random) -> str:
    a_lines = _nonempty_lines(a)
    b_lines = _nonempty_lines(b)
    if not a_lines:
        return b
    if not b_lines:
        return a
    cut_a = rng.randint(1, len(a_lines))
    cut_b = rng.randint(0, max(0, len(b_lines) - 1))
    out = a_lines[:cut_a] + b_lines[cut_b:]
    return "\n".join(out) + "\n"


@dataclass
class Mutator:
    name: str
    fn: MutatorFn
    weight: float = 1.0
    tries: int = 0
    rewards: float = 0.0

    @property
    def score(self) -> float:
        # Thompson-lite optimistic value without extra deps.
        return (self.rewards + 1.0) / (self.tries + 1.0)


class MutatorPool:
    def __init__(self) -> None:
        self._mutators = [
            Mutator("insert_statement", insert_statement, 1.0),
            Mutator("duplicate_block", duplicate_block, 1.0),
            Mutator("tweak_numeric_literal", tweak_numeric_literal, 1.0),
        ]

    def choose(self, rng: random.Random) -> Mutator:
        weighted = [max(0.05, m.weight * m.score) for m in self._mutators]
        return rng.choices(self._mutators, weights=weighted, k=1)[0]

    def reward(self, name: str, delta: float) -> None:
        for m in self._mutators:
            if m.name == name:
                m.tries += 1
                m.rewards += delta
                return

    def names(self) -> list[str]:
        return [m.name for m in self._mutators]


    def stats(self) -> list[dict[str, float | int | str]]:
        return [
            {
                "name": m.name,
                "weight": m.weight,
                "tries": m.tries,
                "rewards": m.rewards,
                "score": m.score,
            }
            for m in self._mutators
        ]
