from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.heatmap import HeatmapPlot


def heatmap_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
    index_col: str = typer.Option(None, help="zh: 用作行索引的列。\nen: Column to use as row index."),
    cluster_rows: bool = typer.Option(True, help="zh: 是否聚类行。\nen: Whether to cluster rows."),
    cluster_cols: bool = typer.Option(True, help="zh: 是否聚类列。\nen: Whether to cluster columns."),
    z_score: int = typer.Option(
        None,
        help="zh: 标准化 (0: 行, 1: 列)。None 禁用。\nen: 0 (rows) or 1 (columns) for standardization. None to disable.",
    ),
    cmap: str = typer.Option(
        None, help="zh: 颜色映射名称 (例如 'vlag', 'coolwarm')。\nen: Colormap name (e.g. 'vlag', 'coolwarm')."
    ),
    center: float = typer.Option(None, help="zh: 颜色映射居中的值。\nen: Value at which to center the colormap."),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
) -> None:
    """
    zh: 生成热图/聚类图。
    en: Generate heatmap/clustermap.
    """
    df = read_data(input_file, sheet=sheet)

    # 准备传递给 plot 的 kwargs，过滤掉 None 的值以允许使用默认值/主题值
    kwargs = {}
    if cmap is not None:
        kwargs["cmap"] = cmap
    if center is not None:
        kwargs["center"] = center

    plotter = HeatmapPlot(theme=theme)
    plotter.plot(
        data=df,
        index_col=index_col,
        cluster_rows=cluster_rows,
        cluster_cols=cluster_cols,
        z_score=z_score,
        title=title,
        output=str(output),
        **kwargs,
    )
    typer.echo(f"Saved heatmap to {output}")
