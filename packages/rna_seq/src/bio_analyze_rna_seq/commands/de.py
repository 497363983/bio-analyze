from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from bio_analyze_rna_seq.de import DEManager


def run_de(
    counts: Path = typer.Option(..., "--counts", help="zh: 计数矩阵 CSV 文件。\nen: Counts matrix CSV file."),
    design: Path = typer.Option(..., "--design", help="zh: 设计矩阵 CSV 文件。\nen: Design matrix CSV file."),
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    theme: str = typer.Option("default", help="zh: 绘图主题。\nen: Plot theme."),
):
    """
    zh: 运行差异表达分析 (DESeq2)。
    en: Run differential expression analysis (DESeq2).
    """
    counts_df = pd.read_csv(counts, index_col=0)
    mgr = DEManager(counts=counts_df, design_file=design, output_dir=output_dir, theme=theme)
    mgr.run()
    typer.echo(f"DE analysis completed. Results in {output_dir}")
