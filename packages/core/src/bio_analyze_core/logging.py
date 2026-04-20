from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger as loguru_logger

_DEFAULT_CONSOLE_SINK_ID = None

def get_logger(
    name: str,
    console_output: bool = True,
    log_path: str | Path | None = None,
    level: str = "INFO",
):
    """
    Get a configured loguru logger instance.

    Note: Loguru has only one global logger object, but we can create context-aware loggers via .bind().
    Here we return a new logger binding. We do NOT reset global sinks anymore.

    Args:
        name (str):
            Logger name (bound to extra["name"]).
        console_output (bool, optional):
            (Deprecated/Ignored) Console output is now managed globally by setup_logging.
        log_path (Optional[str | Path], optional):
            Log file path. If a directory is provided, creates {name}.log inside.
        level (str, optional):
            File log level (default "INFO"). Console level is set by setup_logging.
    """

    # We do NOT remove existing sinks anymore.
    # loguru_logger.remove()

    # We do NOT add a specific console sink for this logger,
    # relying on the global sink configured in setup_logging.
    # If we wanted to respect console_output=False, we would need to ensure the global sink filters this out,
    # or we just accept that console output is global.
    # Given the requirement "Unified initialization", relying on global sink is correct.

    # Add file sink if requested
    if log_path:
        path_obj = Path(log_path)
        is_directory = path_obj.suffix == ""

        if is_directory:
            path_obj.mkdir(parents=True, exist_ok=True)
            log_file = path_obj / f"{name}.log"
        else:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            log_file = path_obj

        # Add file handler
        # enqueue=True ensures multi-process/thread safety
        loguru_logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} {level} {extra[name]}: {message}",
            level=level,
            enqueue=True,
            encoding="utf-8",
            filter=lambda record: record["extra"].get("name") == name,
        )

    return loguru_logger.bind(name=name)

def setup_logging(level: str = "INFO") -> None:
    """
    Initialize or update the default console sink. This operation is idempotent.

    Args:
        level (str, optional):
            Log level (e.g., "DEBUG", "INFO", "WARNING"). Defaults to "INFO".
    """
    global _DEFAULT_CONSOLE_SINK_ID

    # Format that includes the 'name' from extra
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level: <8}</level> "
        "<cyan>{extra[name]}</cyan>: <level>{message}</level>"
    )

    if _DEFAULT_CONSOLE_SINK_ID is None:
        _DEFAULT_CONSOLE_SINK_ID = loguru_logger.add(sys.stderr, level=level, format=fmt)
    else:
        # Update level: remove and recreate default console sink
        loguru_logger.remove(_DEFAULT_CONSOLE_SINK_ID)
        _DEFAULT_CONSOLE_SINK_ID = loguru_logger.add(sys.stderr, level=level, format=fmt)
