from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """获取 logger 实例。"""
    return logging.getLogger(name)

def setup_logging(level: str = "INFO") -> None:
    """配置全局日志级别和格式。"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

