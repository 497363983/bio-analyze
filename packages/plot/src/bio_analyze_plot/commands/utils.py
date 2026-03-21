from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_data(input_path: Path, sheet: str | None = None) -> pd.DataFrame:
    """
    zh: 从 CSV、TSV 或 Excel 文件读取数据。
    en: Read data from CSV, TSV, or Excel file.

    Args:
        input_path (Path):
            zh: 输入文件路径
            en: Input file path
        sheet (str | None, optional):
            zh: Excel 工作表名称
            en: Excel sheet name

    Returns:
        pd.DataFrame:
            zh: 读取的数据
            en: Loaded data
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
