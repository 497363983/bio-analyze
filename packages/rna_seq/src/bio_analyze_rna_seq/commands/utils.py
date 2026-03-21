from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from bio_analyze_rna_seq.qc import QCManager


def load_config(config_file: Path) -> dict[str, Any]:
    """
    zh: 从 JSON 或 YAML 文件加载配置。
    en: Load configuration from JSON or YAML file.

    Args:
        config_file (Path):
            zh: 配置文件路径
            en: Path to configuration file

    Returns:
        dict[str, Any]:
            zh: 配置字典
            en: Configuration dictionary
    """
    if config_file.suffix in (".json",):
        with open(config_file, encoding="utf-8") as f:
            return json.load(f)
    elif config_file.suffix in (".yaml", ".yml"):
        with open(config_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Config file must be .json or .yaml/.yml")


def detect_clean_reads(input_dir: Path) -> dict[str, dict]:
    """
    zh: 从 QC 输出目录检测 clean reads。
    en: Detect clean reads from QC output directory.

    zh: 假设文件命名为 {sample}_clean_R1.fastq.gz
    en: Assumes files are named {sample}_clean_R1.fastq.gz

    Args:
        input_dir (Path):
            zh: 输入目录
            en: Input directory

    Returns:
        dict[str, dict]:
            zh: 样本文件字典
            en: Sample files dictionary
    """
    # 使用 QCManager 的检测逻辑查找文件
    temp_mgr = QCManager(input_dir, input_dir)
    raw_samples = temp_mgr._detect_files(input_dir)

    clean_samples = {}
    for sample, files in raw_samples.items():
        # QCManager 可能会将 "sample_clean" 检测为样本名，如果后缀是 _clean_R1
        # 所以我们从样本名中去除 "_clean"
        real_name = sample.replace("_clean", "")
        clean_samples[real_name] = files

    return clean_samples
