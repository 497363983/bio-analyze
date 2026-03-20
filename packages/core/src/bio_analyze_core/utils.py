import json
import os
import shutil
from pathlib import Path
from typing import Any, Union

import yaml

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # For Python < 3.11


def load_config(config_path: Union[str, Path]) -> dict[str, Any]:
    """
    zh: 加载 JSON, YAML 或 TOML 配置文件。
    en: Load JSON, YAML, or TOML configuration file.

    Args:
        config_path (Union[str, Path]):
            zh: 配置文件路径。
            en: Path to configuration file.

    Returns:
        dict[str, Any]:
            zh: 包含配置数据的字典。
            en: Dictionary containing configuration data.

    Raises:
        FileNotFoundError:
            zh: 如果文件不存在。
            en: If file does not exist.
        ValueError:
            zh: 如果文件格式不支持。
            en: If file format is not supported.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    suffix = path.suffix.lower()
    if suffix in [".json"]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    elif suffix in [".yaml", ".yml"]:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif suffix in [".toml"]:
        with open(path, "rb") as f:
            return tomllib.load(f)
    else:
        raise ValueError(f"Unsupported configuration format: {suffix}. Use .json, .yaml/.yml or .toml")


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    zh: 确保目录存在，如有必要则创建。
    en: Ensure directory exists, create if necessary.

    Args:
        path (Union[str, Path]):
            zh: 目录路径。
            en: Directory path.

    Returns:
        Path:
            zh: 目录的 Path 对象。
            en: Path object of the directory.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def check_tool(tool_name: str) -> bool:
    """
    zh: 检查系统 PATH 中是否可用命令行工具。
    en: Check if a command line tool is available in system PATH.

    Args:
        tool_name (str):
            zh: 工具/命令的名称。
            en: Name of tool/command.

    Returns:
        bool:
            zh: 如果工具存在则为 True，否则为 False。
            en: True if tool exists, False otherwise.
    """
    return shutil.which(tool_name) is not None


def find_files(directory: Union[str, Path], patterns: list[str], recursive: bool = False) -> list[Path]:
    """
    zh: 在目录中查找匹配给定 glob 模式的文件。
    en: Find files matching given glob patterns in a directory.

    Args:
        directory (Union[str, Path]):
            zh: 要搜索的目录。
            en: Directory to search.
        patterns (list[str]):
            zh: glob 模式列表（例如 ["*.txt", "*.csv"]）。
            en: List of glob patterns (e.g. ["*.txt", "*.csv"]).
        recursive (bool, optional):
            zh: 是否递归搜索（使用 rglob）。默认为 False。
            en: Whether to search recursively (use rglob). Defaults to False.

    Returns:
        list[Path]:
            zh: 匹配模式的唯一 Path 对象的排序列表。
            en: Sorted list of unique Path objects matching patterns.
    """
    d = Path(directory)
    if not d.exists() or not d.is_dir():
        return []

    files = []
    for pattern in patterns:
        if recursive:
            files.extend(d.rglob(pattern))
        else:
            files.extend(d.glob(pattern))

    return sorted(list(set(files)))


def json_serializer(obj: Any) -> Any:
    """
    zh: 用于默认 json 代码不可序列化对象的 JSON 序列化器。处理 Path 对象。
    en: JSON serializer for objects not serializable by default json code. Handles Path objects.

    Args:
        obj (Any):
            zh: 要序列化的对象。
            en: Object to serialize.

    Returns:
        Any:
            zh: 序列化后的对象。
            en: Serialized object.
    """
    if isinstance(obj, (Path, os.PathLike)):
        return str(obj)
    return json.dumps(obj)


def safe_save_json(data: Any, path: Union[str, Path], **kwargs):
    """
    zh: 原子地将数据保存到 JSON 文件。
    en: Atomically save data to JSON file.

    Args:
        data (Any):
            zh: 要保存的数据（必须是 JSON 可序列化的）。
            en: Data to save (must be JSON serializable).
        path (Union[str, Path]):
            zh: 输出文件路径。
            en: Output file path.
        **kwargs:
            zh: 传递给 json.dump 的附加参数。
            en: Additional arguments passed to json.dump.
    """
    path = Path(path)
    temp_path = path.with_suffix(path.suffix + ".tmp")

    # 设置默认 kwargs
    if "default" not in kwargs:
        kwargs["default"] = json_serializer
    if "ensure_ascii" not in kwargs:
        kwargs["ensure_ascii"] = False
    if "indent" not in kwargs:
        kwargs["indent"] = 2

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, **kwargs)

        if path.exists():
            path.unlink()
        temp_path.rename(path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def safe_load_json(path: Union[str, Path]) -> Any:
    """
    zh: 从 JSON 文件加载数据。
    en: Load data from JSON file.

    Args:
        path (Union[str, Path]):
            zh: 输入文件路径。
            en: Input file path.

    Returns:
        Any:
            zh: 加载的数据。
            en: Loaded data.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)
