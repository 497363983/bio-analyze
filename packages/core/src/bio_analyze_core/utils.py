import json
import os
import shutil
from pathlib import Path
from typing import Any, Union

import yaml


def load_config(config_path: Union[str, Path]) -> dict[str, Any]:
    """
    加载 JSON 或 YAML 配置文件。

    Args:
        config_path: 配置文件路径。

    Returns:
        包含配置数据的字典。

    Raises:
        FileNotFoundError: 如果文件不存在。
        ValueError: 如果文件格式不支持。
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
    else:
        raise ValueError(f"Unsupported configuration format: {suffix}. Use .json or .yaml/.yml")


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    确保目录存在，如有必要则创建。

    Args:
        path: 目录路径。

    Returns:
        目录的 Path 对象。
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def check_tool(tool_name: str) -> bool:
    """
    检查系统 PATH 中是否可用命令行工具。

    Args:
        tool_name: 工具/命令的名称。

    Returns:
        如果工具存在则为 True，否则为 False。
    """
    return shutil.which(tool_name) is not None


def find_files(directory: Union[str, Path], patterns: list[str], recursive: bool = False) -> list[Path]:
    """
    在目录中查找匹配给定 glob 模式的文件。

    Args:
        directory: 要搜索的目录。
        patterns: glob 模式列表（例如 ["*.txt", "*.csv"]）。
        recursive: 是否递归搜索（使用 rglob）。

    Returns:
        匹配模式的唯一 Path 对象的排序列表。
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
    用于默认 json 代码不可序列化对象的 JSON 序列化器。
    处理 Path 对象。
    """
    if isinstance(obj, (Path, os.PathLike)):
        return str(obj)
    return json.dumps(obj)


def safe_save_json(data: Any, path: Union[str, Path], **kwargs):
    """
    原子地将数据保存到 JSON 文件。

    Args:
        data: 要保存的数据（必须是 JSON 可序列化的）。
        path: 输出文件路径。
        **kwargs: 传递给 json.dump 的附加参数。
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
    从 JSON 文件加载数据。

    Args:
        path: 输入文件路径。

    Returns:
        加载的数据。
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)
