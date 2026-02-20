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

    @property
    def crashed(self) -> bool:
        return (not self.timed_out) and self.returncode != 0

    @property
    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(str(self.returncode).encode())
        h.update(self.stdout.encode(errors="ignore"))
        h.update(self.stderr.encode(errors="ignore"))
        return h.hexdigest()


class D8Runner:
    def __init__(self, d8_path: str, timeout_sec: float = 1.0) -> None:
        self.d8_path = d8_path
        self.timeout_sec = timeout_sec

    def run(self, program_path: Path) -> RunResult:
        cmd = [self.d8_path, "--allow-natives-syntax", "--expose-gc", str(program_path)]
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
            )
        except subprocess.TimeoutExpired as exc:
            return RunResult(
                returncode=-1,
                timed_out=True,
                stdout=(exc.stdout or ""),
                stderr=(exc.stderr or ""),
            )
