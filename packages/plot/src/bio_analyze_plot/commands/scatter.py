from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.scatter import ScatterPlot


def scatter_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
    x: str = typer.Option(..., help="zh: X 轴列名。\nen: Column name for X-axis."),
    y: str = typer.Option(..., help="zh: Y 轴列名。\nen: Column name for Y-axis."),
    hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
    style: str = typer.Option(None, help="zh: 标记样式列名。\nen: Column name for marker style."),
    size: str = typer.Option(None, help="zh: 标记大小列名。\nen: Column name for marker size."),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    add_ellipse: bool = typer.Option(
        False, help="zh: 为每个分组绘制置信椭圆。\nen: Draw confidence ellipses for each group."
    ),
    ellipse_std: float = typer.Option(
        2.0, help="zh: 置信椭圆的标准差。\nen: Standard deviation for confidence ellipses."
    ),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
) -> None:
    """
    zh: 生成散点图。
    en: Generate scatter plot.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = ScatterPlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        style=style,
        size=size,
        title=title,
        output=str(output),
        add_ellipse=add_ellipse,
        ellipse_std=ellipse_std,
    )
    typer.echo(f"Saved scatter plot to {output}")
