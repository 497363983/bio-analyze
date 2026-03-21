from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.pie import PiePlot


def pie_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
    x: str = typer.Option(..., help="zh: 标签列名 (分类变量)。\nen: Column name for labels (categorical)."),
    y: str = typer.Option(..., help="zh: 数值列名。\nen: Column name for values (numerical)."),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    autopct: str = typer.Option("%1.1f%%", help="zh: 百分比格式。\nen: Percentage format."),
    startangle: float = typer.Option(90, help="zh: 起始角度。\nen: Start angle."),
    explode: str = typer.Option(
        None,
        help="zh: 扇区偏移。可以是列名或逗号分隔的数值。\nen: Explode slices. Can be a column name or comma-separated values.",
    ),
    shadow: bool = typer.Option(False, help="zh: 显示阴影。\nen: Show shadow."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
) -> None:
    """
    zh: 生成饼图。
    en: Generate pie chart.
    """
    df = read_data(input_file, sheet=sheet)

    explode_arg = None
    if explode:
        if explode in df.columns:
            explode_arg = explode
        else:
            try:
                explode_arg = [float(v.strip()) for v in explode.split(",")]
            except ValueError:
                explode_arg = None
                typer.echo(f"Warning: Invalid explode format '{explode}'. Ignored.")

    plotter = PiePlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        title=title,
        autopct=autopct,
        startangle=startangle,
        explode=explode_arg,
        shadow=shadow,
        output=str(output),
    )
    typer.echo(f"Saved pie chart to {output}")
