from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.chromosome import ChromosomePlot


def chromosome_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
    chrom_col: str = typer.Option("chrom", help="zh: 染色体列名。\nen: Column name for chromosome."),
    pos_col: str = typer.Option("pos", help="zh: 位置列名。\nen: Column name for position."),
    pos_counts_col: str = typer.Option(
        "pos_counts", help="zh: 正链计数列名。\nen: Column name for positive strand counts."
    ),
    neg_counts_col: str = typer.Option(
        "neg_counts", help="zh: 负链计数列名。\nen: Column name for negative strand counts."
    ),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    max_chroms: int = typer.Option(
        24, help="zh: 显示的最大染色体数量。\nen: Maximum number of chromosomes to display."
    ),
) -> None:
    """
    zh: 生成染色体覆盖度分布图。
    en: Generate chromosome coverage distribution plot.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = ChromosomePlot(theme=theme)
    plotter.plot(
        data=df,
        chrom_col=chrom_col,
        pos_col=pos_col,
        pos_counts_col=pos_counts_col,
        neg_counts_col=neg_counts_col,
        max_chroms=max_chroms,
        title=title,
        output=str(output),
    )
    typer.echo(f"Saved chromosome plot to {output}")
