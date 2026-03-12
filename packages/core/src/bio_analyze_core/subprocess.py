from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass

# Export CalledProcessError for consumers
CalledProcessError = subprocess.CalledProcessError


@dataclass(frozen=True, slots=True)
class CommandResult:
    """命令执行结果。"""

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
    capture_output: bool = True,
    text: bool = True,
) -> CommandResult:
    """
    运行子进程命令。

    Args:
        args: 命令参数列表。
        cwd: 工作目录。
        env: 环境变量。
        check: 如果为 True 且返回码非零，则抛出 CalledProcessError。
        capture_output: 是否捕获标准输出和标准错误。
        text: 是否以文本模式运行。

    Returns:
        CommandResult 对象。
    """
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        env=env,
        check=False,
        text=text,
        capture_output=capture_output,
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
