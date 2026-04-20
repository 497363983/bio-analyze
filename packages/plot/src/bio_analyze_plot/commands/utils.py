from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_data(input_path: Path, sheet: str | None = None) -> pd.DataFrame:
    """
    Read data from CSV, TSV, or Excel file.

    Args:
        input_path (Path):
            Input file path
        sheet (str | None, optional):
            Excel sheet name

    Returns:
        pd.DataFrame:
            Loaded data
    """
    suffix = input_path.suffix.lower()
    if suffix in [".csv"]:
        return pd.read_csv(input_path)
    elif suffix in [".tsv", ".txt"]:
        return pd.read_csv(input_path, sep="\t")
    elif suffix in [".xlsx", ".xls"]:
        if sheet:
            return pd.read_excel(input_path, sheet_name=sheet)
        return pd.read_excel(input_path)
    else:
        # 默认为 csv
        return pd.read_csv(input_path)
