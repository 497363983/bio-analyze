from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib
from typing import Any


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "bio-analyze" / "config.toml"


def _load_toml(path: Path) -> dict[str, Any]:
    """加载 TOML 配置文件。"""
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True, slots=True)
class Settings:
    """全局配置类。"""
    data_dir: Path | None = None
    work_dir: Path | None = None
    log_level: str = "INFO"


def load_settings(config_path: Path | None = None) -> Settings:
    """加载配置。优先级：环境变量 > 命令行参数 > 默认文件。"""
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

