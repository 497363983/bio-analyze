from __future__ import annotations

import os
try:
    import tomllib
except ImportError:
    import tomli as tomllib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "bio-analyze" / "config.toml"


def _load_toml(path: Path) -> dict[str, Any]:
    """
    zh: 加载 TOML 配置文件。
    en: Load TOML configuration file.

    Args:
        path (Path):
            zh: 配置文件路径。
            en: Path to configuration file.

    Returns:
        dict[str, Any]:
            zh: 解析后的配置字典。
            en: Parsed configuration dictionary.
    """
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True, **({"slots": True} if sys.version_info >= (3, 10) else {}))
class Settings:
    """
    zh: 全局配置类。
    en: Global settings class.

    Attributes:
        data_dir (Path | None):
            zh: 数据目录路径。
            en: Path to data directory.
        work_dir (Path | None):
            zh: 工作目录路径。
            en: Path to working directory.
        log_level (str):
            zh: 日志级别（默认 "INFO"）。
            en: Log level (default "INFO").
    """

    data_dir: Path | None = None
    work_dir: Path | None = None
    log_level: str = "INFO"


def load_settings(config_path: Path | None = None) -> Settings:
    """
    zh: 加载配置。优先级：环境变量 > 命令行参数 > 默认文件。
    en: Load settings. Priority: Environment variables > Command line arguments > Default file.

    Args:
        config_path (Path | None, optional):
            zh: 配置文件路径。如果未提供，则尝试使用环境变量或默认路径。
            en: Path to configuration file. If not provided, tries to use environment variable or default path.

    Returns:
        Settings:
            zh: 加载后的 Settings 对象。
            en: Loaded Settings object.
    """
    path_str = os.environ.get("BIO_ANALYSE_CONFIG")
    resolved_path = Path(path_str) if path_str else (config_path or DEFAULT_CONFIG_PATH)

    raw = _load_toml(resolved_path)
    cfg = raw.get("bio_analyze", {})

    data_dir = cfg.get("data_dir")
    work_dir = cfg.get("work_dir")
    log_level = cfg.get("log_level", "INFO")

    return Settings(
        data_dir=Path(data_dir) if data_dir else None,
        work_dir=Path(work_dir) if work_dir else None,
        log_level=str(log_level),
    )
