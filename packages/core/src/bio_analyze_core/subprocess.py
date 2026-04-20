from __future__ import annotations

import contextlib
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass

from .logging import get_logger

logger = get_logger(__name__)

# Export CalledProcessError for consumers
CalledProcessError = subprocess.CalledProcessError
TimeoutExpired = subprocess.TimeoutExpired

@dataclass(frozen=True, **({"slots": True} if sys.version_info >= (3, 10) else {}))
class CommandResult:
    """
    Command execution result wrapper class.

    Attributes:
        args (Sequence[str]):
            List of command arguments executed.
        returncode (int):
            Process return code (0 indicates success).
        stdout (str | bytes):
            Standard output content.
        stderr (str | bytes):
            Standard error content.
    """

    args: Sequence[str]
    returncode: int
    stdout: str | bytes
    stderr: str | bytes

def run(
    args: Sequence[str],
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
    timeout: float | None = None,
    tail_lines: int = 50,
    echo: bool = True,
    encoding: str | None = "utf-8",
) -> CommandResult:
    """
    Run a subprocess command.

    Args:
        args (Sequence[str]):
            List of command arguments.
        cwd (str | None, optional):
            Working directory path.
        env (dict[str, str] | None, optional):
            Environment variables dictionary.
        check (bool, optional):
            If True, raise CalledProcessError if return code is non-zero. Defaults to True.
        capture_output (bool, optional):
            Whether to capture stdout and stderr. Defaults to True.
        text (bool, optional):
            Whether to run in text mode (return str instead of bytes). Defaults to True.
        timeout (float | None, optional):
            Timeout in seconds. Defaults to None (no timeout).
        tail_lines (int, optional):
            Number of trailing lines to include in the error message on failure. Defaults to 50.
        echo (bool, optional):
            Whether to log the executed command. Defaults to True.

    Returns:
        CommandResult:
            Command execution result object.

    Raises:
        CalledProcessError:
            Raised when check=True and command returns non-zero exit code.
        TimeoutExpired:
            Raised when the command execution times out.
    """
    if echo:
        logger.debug(f"Executing command: {' '.join(str(x) for x in args)}")

    start_time = time.perf_counter()
    try:
        completed = subprocess.run(
            list(args),
            cwd=cwd,
            env=env,
            check=False,
            text=text,
            capture_output=capture_output,
            timeout=timeout,
            encoding=encoding,
        )
    except subprocess.TimeoutExpired as e:
        duration = time.perf_counter() - start_time
        logger.error(f"Command timed out after {duration:.2f}s: {' '.join(str(x) for x in args)}")

        # Format trailing output
        output_str = ""
        if e.output:
            if isinstance(e.output, bytes):
                with contextlib.suppress(Exception):
                    output_str = e.output.decode("utf-8", errors="replace")
            else:
                output_str = str(e.output)

        tail = "\n".join(output_str.splitlines()[-tail_lines:]) if output_str else ""
        raise subprocess.TimeoutExpired(
            cmd=e.cmd,
            timeout=e.timeout,
            output=tail.encode("utf-8") if isinstance(e.output, bytes) else tail,
            stderr=e.stderr,
        ) from None

    if check and completed.returncode != 0:
        duration = time.perf_counter() - start_time
        logger.error(
            "Command failed with exit code %s after %.2fs: %s",
            completed.returncode,
            duration,
            " ".join(str(x) for x in args),
        )

        # Format trailing stdout
        stdout_str = ""
        if completed.stdout:
            if isinstance(completed.stdout, bytes):
                with contextlib.suppress(Exception):
                    stdout_str = completed.stdout.decode("utf-8", errors="replace")
            else:
                stdout_str = str(completed.stdout)

        # Format trailing stderr
        stderr_str = ""
        if completed.stderr:
            if isinstance(completed.stderr, bytes):
                with contextlib.suppress(Exception):
                    stderr_str = completed.stderr.decode("utf-8", errors="replace")
            else:
                stderr_str = str(completed.stderr)

        tail_out = "\n".join(stdout_str.splitlines()[-tail_lines:]) if stdout_str else ""
        tail_err = "\n".join(stderr_str.splitlines()[-tail_lines:]) if stderr_str else ""

        raise subprocess.CalledProcessError(
            completed.returncode,
            completed.args,
            output=tail_out.encode("utf-8") if isinstance(completed.stdout, bytes) else tail_out,
            stderr=tail_err.encode("utf-8") if isinstance(completed.stderr, bytes) else tail_err,
        )

    return CommandResult(
        args=tuple(str(x) for x in args),
        returncode=completed.returncode,
        stdout=completed.stdout or ("" if text else b""),
        stderr=completed.stderr or ("" if text else b""),
    )

def run_streaming(
    args: Sequence[str],
    on_stdout: callable,
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
    tail_lines: int = 50,
    echo: bool = True,
    encoding: str | None = "utf-8",
) -> CommandResult:
    """
    Run a subprocess command with streaming, reading output line by line.

    Args:
        args (Sequence[str]):
            List of command arguments.
        on_stdout (callable):
            Callback function to handle each line of stdout, taking a string argument.
        cwd (str | None, optional):
            Working directory path.
        env (dict[str, str] | None, optional):
            Environment variables dictionary.
        timeout (float | None, optional):
            Timeout in seconds. Defaults to None (no timeout).
        tail_lines (int, optional):
            Number of trailing lines to include in the error message on failure. Defaults to 50.
        echo (bool, optional):
            Whether to log the executed command. Defaults to True.

    Returns:
        CommandResult:
            Command execution result object (stdout will be empty due to streaming).

    Raises:
        CalledProcessError:
            Raised when command returns non-zero exit code.
        TimeoutExpired:
            Raised when the command execution times out.
    """
    if echo:
        logger.debug(f"Executing command (streaming): {' '.join(str(x) for x in args)}")

    start_time = time.perf_counter()
    history = []

    with subprocess.Popen(
        list(args),
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        encoding=encoding,
    ) as p:
        import threading

        timer = None
        timeout_expired = [False]
        if timeout is not None:

            def kill_proc():
                timeout_expired[0] = True
                p.kill()

            timer = threading.Timer(timeout, kill_proc)
            timer.start()

        try:
            for line in p.stdout:
                line_str = line.rstrip()
                on_stdout(line_str)
                history.append(line_str)
                if len(history) > tail_lines:
                    history.pop(0)
            p.wait()
        finally:
            if timer is not None:
                timer.cancel()

        if timeout_expired[0]:
            duration = time.perf_counter() - start_time
            logger.error(f"Command timed out after {duration:.2f}s: {' '.join(str(x) for x in args)}")
            raise subprocess.TimeoutExpired(cmd=list(args), timeout=timeout, output="\n".join(history))

    if p.returncode != 0:
        duration = time.perf_counter() - start_time
        logger.error(
            f"Command failed with exit code {p.returncode} after {duration:.2f}s: {' '.join(str(x) for x in args)}"
        )
        raise subprocess.CalledProcessError(p.returncode, list(args), output="\n".join(history))

    return CommandResult(
        args=tuple(str(x) for x in args),
        returncode=p.returncode,
        stdout="",
        stderr="",
    )
