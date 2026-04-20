from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from bio_analyze_core.cli.app import prompt
from bio_analyze_core.i18n import _
from bio_analyze_core.logging import get_logger
from bio_analyze_omics.rna_seq.genome import genomepy
from bio_analyze_omics.rna_seq.qc import QCManager

logger = get_logger(__name__)


def _is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, float):
        return math.isnan(value)
    return False


def _pick_first_value(record: Mapping[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = record.get(key)
        if not _is_missing_value(value):
            return value
    return None


def _normalize_search_results(results: Any) -> list[dict[str, Any]]:
    sequence_columns = [
        "name",
        "provider",
        "accession",
        "tax_id",
        "annotation",
        "species",
        "description",
    ]

    if results is None:
        return []
    if hasattr(results, "to_dict"):
        try:
            records = results.to_dict(orient="records")
        except TypeError:
            records = results.to_dict("records")
        return [dict(record) for record in records]
    if isinstance(results, list):
        normalized = []
        for item in results:
            if isinstance(item, Mapping):
                normalized.append(dict(item))
            elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
                row = {
                    column: item[index]
                    for index, column in enumerate(sequence_columns)
                    if index < len(item)
                }
                if row:
                    normalized.append(row)
        return normalized
    return []


def search_and_select_reference(species: str) -> tuple[str, str | None]:
    """Search reference genomes by species and let the user select in the CLI."""
    if genomepy is None:
        raise RuntimeError("genomepy is not installed or failed to import. Cannot search genomes.")
    res = list(genomepy.search(species))
    logger.info(res)
    results = _normalize_search_results(res)
    if not results:
        raise RuntimeError(f"No genome search results found for species: {species}")

    logger.info("Genome search results for '%s': %s", species, results)
    selection = prompt(
        _("Select the reference genome number to download"),
        type=int,
        default=1,
    )
    if selection < 1 or selection > len(results):
        raise ValueError(f"Selection must be between 1 and {len(results)}.")

    record = results[selection - 1]
    query = _pick_first_value(record, ["name", "genome", "assembly_name"])
    accession = _pick_first_value(record, ["accession", "assembly_accession", "assembly", "accession_id"])
    if _is_missing_value(query):
        query = accession
    if _is_missing_value(query):
        raise RuntimeError(f"Selected search result does not contain a downloadable genome identifier: {record}")

    provider = _pick_first_value(record, ["provider", "source", "database"])
    logger.info(
        "Selected genome search result: query=%s, accession=%s, provider=%s",
        query,
        accession or "-",
        provider or "auto",
    )
    return str(query), str(provider) if not _is_missing_value(provider) else None


def load_config(config_file: Path) -> dict[str, Any]:
    """
    Load configuration from a JSON or YAML file.

    Args:
        config_file (Path): Path to the configuration file.

    Returns:
        dict[str, Any]: Configuration dictionary.
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
    Detect clean reads from the QC output directory.

    Assumes files are named `{sample}_clean_R1.fastq.gz`.

    Args:
        input_dir (Path): Input directory.

    Returns:
        dict[str, dict]: Sample files dictionary.
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
