from __future__ import annotations

from typing import Callable


Predicate = Callable[[str], bool]


def minimize_by_lines(program: str, is_interesting: Predicate, max_passes: int = 8) -> str:
    """Simple line-based delta debugging.

    Keeps removing chunks while predicate remains true.
    """
    lines = [ln for ln in program.splitlines() if ln.strip()]
    if not lines:
        return program
    if not is_interesting("\n".join(lines) + "\n"):
        return program

    granularity = 2
    passes = 0
    while granularity <= max(2, len(lines)) and passes < max_passes:
        passes += 1
        chunk = max(1, len(lines) // granularity)
        reduced = False

        i = 0
        while i < len(lines):
            trial = lines[:i] + lines[i + chunk :]
            if trial and is_interesting("\n".join(trial) + "\n"):
                lines = trial
                reduced = True
                # same granularity again to aggressively shrink
            else:
                i += chunk

        if not reduced:
            granularity *= 2

    return "\n".join(lines) + "\n"
