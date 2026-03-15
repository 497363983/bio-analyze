from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass

# Export CalledProcessError for consumers
CalledProcessError = subprocess.CalledProcessError


@dataclass(frozen=True, slots=True)
class CommandResult:
    """
    zh: 命令执行结果封装类。
    en: Command execution result wrapper class.

    Attributes:
        args (Sequence[str]):
            zh: 执行的命令参数列表。
            en: List of command arguments executed.
        returncode (int):
            zh: 进程返回码（0 表示成功）。
            en: Process return code (0 indicates success).
        stdout (str):
            zh: 标准输出内容。
            en: Standard output content.
        stderr (str):
            zh: 标准错误内容。
            en: Standard error content.
    """

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
    zh: 运行子进程命令。
    en: Run a subprocess command.

    Args:
        args (Sequence[str]):
            zh: 命令参数列表。
            en: List of command arguments.
        cwd (str | None, optional):
            zh: 工作目录路径。
            en: Working directory path.
        env (dict[str, str] | None, optional):
            zh: 环境变量字典。
            en: Environment variables dictionary.
        check (bool, optional):
            zh: 如果为 True 且返回码非零，则抛出 CalledProcessError。默认为 True。
            en: If True, raise CalledProcessError if return code is non-zero. Defaults to True.
        capture_output (bool, optional):
            zh: 是否捕获标准输出和标准错误。默认为 True。
            en: Whether to capture stdout and stderr. Defaults to True.
        text (bool, optional):
            zh: 是否以文本模式运行（返回 str 而非 bytes）。默认为 True。
            en: Whether to run in text mode (return str instead of bytes). Defaults to True.

    Returns:
        CommandResult:
            zh: 命令执行结果对象。
            en: Command execution result object.

    Raises:
        CalledProcessError:
            zh: 当 check=True 且命令返回非零退出码时抛出。
            en: Raised when check=True and command returns non-zero exit code.
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
