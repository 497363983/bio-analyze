from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Iterable, Sequence


@dataclass(frozen=True, slots=True)
class CommandResult:
    args: Sequence[str]
    returncode: int
    stdout: str
    stderr: str


def run(
    args: Sequence[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> CommandResult:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            completed.args,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return CommandResult(
        args=tuple(str(x) for x in args),
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )

