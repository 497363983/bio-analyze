from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from loguru import logger as loguru_logger


def get_logger(
    name: str,
    console_output: bool = True,
    log_path: Optional[str | Path] = None,
    level: str = "INFO",
):
    """
    获取配置好的 loguru logger 实例。

    注意：Loguru 只有一个全局 logger 对象，但可以通过 .bind() 创建带有上下文的 logger。
    这里我们返回一个新的 logger 绑定，但在此之前我们配置全局 logger 的 sink。

    然而，Loguru 的配置是全局的。如果我们在多进程环境中，每个进程都有自己的 Loguru 实例。

    Args:
        name: Logger 名称 (绑定到 extra["name"])
        console_output: 是否输出到控制台 (注意：这会影响全局配置，除非我们使用 filter)
        log_path: 日志文件路径
        level: 日志级别
    """
    # 移除默认的 sink (stderr)
    loguru_logger.remove()

    # 重新添加控制台 sink (如果需要)
    if console_output:
        loguru_logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level: <8}</level> <cyan>{extra[name]}</cyan>: <level>{message}</level>",
            level=level,
            filter=lambda record: record["extra"].get("name") == name if name else True,
        )

    # 添加文件 sink
    if log_path:
        path_obj = Path(log_path)

        # 判断是目录还是文件
        is_directory = path_obj.suffix == ""

        if is_directory:
            path_obj.mkdir(parents=True, exist_ok=True)
            log_file = path_obj / f"{name}.log"
        else:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            log_file = path_obj

        # 添加文件 handler
        # enqueue=True 确保多进程/多线程安全
        loguru_logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} {level} {extra[name]}: {message}",
            level=level,
            enqueue=True,
            encoding="utf-8",
            filter=lambda record: record["extra"].get("name") == name,
        )

    # 返回绑定了 name 的 logger
    return loguru_logger.bind(name=name)


def setup_logging(level: str = "INFO") -> None:
    """配置全局日志级别。"""
    # Loguru 默认已经配置好了，这里主要是为了兼容旧接口
    # 我们可以设置默认级别
    loguru_logger.remove()
    loguru_logger.add(sys.stderr, level=level)
