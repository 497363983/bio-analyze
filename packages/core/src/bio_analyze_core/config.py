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
    Load TOML configuration file.

    Args:
        path (Path):
            Path to configuration file.

    Returns:
        dict[str, Any]:
            Parsed configuration dictionary.
    """
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))

@dataclass(frozen=True, **({"slots": True} if sys.version_info >= (3, 10) else {}))
class Settings:
    """
    Global settings class.

    Attributes:
        data_dir (Path | None):
            Path to data directory.
        work_dir (Path | None):
            Path to working directory.
        log_level (str):
            Log level (default "INFO").
    """

    data_dir: Path | None = None
    work_dir: Path | None = None
    log_level: str = "INFO"
    language: str | None = None
    dev_mode: bool = False

def load_settings(config_path: Path | None = None) -> Settings:
    """
    Load settings. Priority: Environment variables > Command line arguments > Default file.

    Args:
        config_path (Path | None, optional):
            Path to configuration file. If not provided, tries to use environment variable or default path.

    Returns:
        Settings:
            Loaded Settings object.
    """
    path_str = os.environ.get("BIO_ANALYSE_CONFIG")
    resolved_path = Path(path_str) if path_str else (config_path or DEFAULT_CONFIG_PATH)

    raw = _load_toml(resolved_path)
    cfg = raw.get("bio_analyze", {})

    data_dir = cfg.get("data_dir")
    work_dir = cfg.get("work_dir")
    log_level = cfg.get("log_level", "INFO")
    language = os.environ.get("BIO_ANALYZE_LANGUAGE") or cfg.get("language")
    dev_mode_raw = os.environ.get("BIO_ANALYZE_DEV_MODE")
    dev_mode = (
        str(dev_mode_raw).lower() in {"1", "true", "yes", "on"}
        if dev_mode_raw is not None
        else bool(cfg.get("dev_mode", False))
    )

    return Settings(
        data_dir=Path(data_dir) if data_dir else None,
        work_dir=Path(work_dir) if work_dir else None,
        log_level=str(log_level),
        language=str(language) if language else None,
        dev_mode=bool(dev_mode),
    )
