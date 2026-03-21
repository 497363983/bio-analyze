from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.line import LinePlot


def line_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
    x: str = typer.Option(..., help="zh: X 轴列名。\nen: Column name for X-axis."),
    y: str = typer.Option(..., help="zh: Y 轴列名。\nen: Column name for Y-axis."),
    hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    error_bar_type: str = typer.Option(None, help="zh: 误差棒类型: SD, SE, CI。\nen: Error bar type: SD, SE, CI."),
    error_bar_ci: float = typer.Option(
        95, help="zh: 置信区间大小 (默认: 95)。\nen: Confidence interval size (default: 95)."
    ),
    error_bar_capsize: float = typer.Option(
        3.0, help="zh: 误差棒帽大小 (以点为单位)。\nen: Error bar capsize (in points)."
    ),
    markers: bool = typer.Option(
        False, help="zh: 为数据点使用默认标记。\nen: Use default markers for data points."
    ),
    marker_style: str = typer.Option(
        None,
        help="zh: 指定标记符号 (逗号分隔, 例如 'o,s')。覆盖 --markers。\nen: Specific marker symbols (comma-separated, e.g. 'o,s'). Overrides --markers.",
    ),
    dashes: bool = typer.Option(True, help="zh: 为线条使用虚线样式。\nen: Use dashes for lines."),
    smooth: bool = typer.Option(False, help="zh: 启用平滑曲线拟合。\nen: Enable smooth curve fitting."),
    smooth_points: int = typer.Option(300, help="zh: 插值点数。\nen: Number of points for interpolation."),
) -> None:
    """
    zh: 生成折线图。
    en: Generate line plot.
    """
    df = read_data(input_file, sheet=sheet)

    # Parse markers
    markers_arg = markers
    if marker_style:
        if "," in marker_style:
            markers_arg = [m.strip() for m in marker_style.split(",")]
        else:
            markers_arg = marker_style

    plotter = LinePlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        title=title,
        output=str(output),
        error_bar_type=error_bar_type,
        error_bar_ci=error_bar_ci,
        error_bar_capsize=error_bar_capsize,
        markers=markers_arg,
        dashes=dashes,
        smooth=smooth,
        smooth_points=smooth_points,
    )
    typer.echo(f"Saved line plot to {output}")
