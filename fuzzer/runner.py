from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunResult:
    returncode: int
    timed_out: bool
    stdout: str
    stderr: str
    cmdline: list[str]

    @property
    def crashed(self) -> bool:
        return (not self.timed_out) and self.returncode not in (0,)

    @property
    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(" ".join(self.cmdline).encode())
        h.update(str(self.returncode).encode())
        h.update(self.stdout.encode(errors="ignore"))
        h.update(self.stderr.encode(errors="ignore"))
        return h.hexdigest()


class D8Runner:
    def __init__(self, d8_path: str, timeout_sec: float = 1.0, flags: list[str] | None = None) -> None:
        self.d8_path = d8_path
        self.timeout_sec = timeout_sec
        self.flags = flags or []

    def _cmd(self, program_path: Path, extra_flags: list[str] | None = None) -> list[str]:
        return [self.d8_path, "--allow-natives-syntax", "--expose-gc", *self.flags, *(extra_flags or []), str(program_path)]

    def run(self, program_path: Path, extra_flags: list[str] | None = None) -> RunResult:
        cmd = self._cmd(program_path, extra_flags=extra_flags)
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                check=False,
            )
            return RunResult(
                returncode=proc.returncode,
                timed_out=False,
                stdout=proc.stdout,
                stderr=proc.stderr,
                cmdline=cmd,
            )
        except subprocess.TimeoutExpired as exc:
            return RunResult(
                returncode=-1,
                timed_out=True,
                stdout=(exc.stdout or ""),
                stderr=(exc.stderr or ""),
                cmdline=cmd,
            )

    def version(self) -> str:
        proc = subprocess.run(
            [self.d8_path, "--version"],
            capture_output=True,
            text=True,
            timeout=self.timeout_sec,
            check=False,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        return out or err or "unknown"


def differential_interesting(primary: RunResult, secondary: RunResult) -> bool:
    if primary.timed_out != secondary.timed_out:
        return True
    if primary.returncode != secondary.returncode:
        return True
    return (primary.stdout != secondary.stdout) or (primary.stderr != secondary.stderr)
