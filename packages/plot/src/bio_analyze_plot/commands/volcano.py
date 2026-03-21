from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.volcano import VolcanoPlot


def volcano_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(
        ...,
        "-o",
        "--output",
        help="zh: 输出文件路径 (例如 volcano.png)。\nen: Output file path (e.g. volcano.png).",
    ),
    x: str = typer.Option(
        "log2FoldChange", help="zh: log2 fold change 列名。\nen: Column name for log2 fold change."
    ),
    y: str = typer.Option("pvalue", help="zh: p-value 列名。\nen: Column name for p-value."),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    fc_cutoff: float = typer.Option(1.0, help="zh: Fold change 截断值。\nen: Fold change cutoff."),
    p_cutoff: float = typer.Option(0.05, help="zh: P-value 截断值。\nen: P-value cutoff."),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
) -> None:
    """
    zh: 从数据生成火山图。
    en: Generate volcano plot from data.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = VolcanoPlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        fc_cutoff=fc_cutoff,
        p_cutoff=p_cutoff,
        title=title,
        output=str(output),
    )
    typer.echo(f"Saved volcano plot to {output}")
