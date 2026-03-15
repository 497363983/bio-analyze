"""
zh: 生物分析核心工具包。
en: Bio-analysis core toolkit.

zh: 包含配置、日志、子进程管理和管道抽象。
en: Contains configuration, logging, subprocess management, and pipeline abstractions.
"""

from .config import Settings, load_settings
from .logging import setup_logging

__all__ = ["Settings", "load_settings", "setup_logging"]
