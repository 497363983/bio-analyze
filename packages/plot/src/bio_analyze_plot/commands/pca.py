from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.pca import PCAPlot


def pca_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
    hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
    style: str = typer.Option(None, help="zh: 标记样式列名。\nen: Column name for marker style."),
    size: str = typer.Option(None, help="zh: 标记大小列名。\nen: Column name for marker size."),
    index_col: str = typer.Option(
        None, help="zh: 用作索引的列 (例如基因名)。\nen: Column to use as index (e.g. gene names)."
    ),
    transpose: bool = typer.Option(
        True,
        help="zh: 转置输入数据 (默认: True, 假设 Genes x Samples)。\nen: Transpose input data (default: True, assumes Genes x Samples).",
    ),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    cluster: bool = typer.Option(False, help="zh: 执行 KMeans 聚类。\nen: Perform KMeans clustering."),
    n_clusters: int = typer.Option(3, help="zh: KMeans 聚类的簇数。\nen: Number of clusters for KMeans."),
    add_ellipse: bool = typer.Option(
        False, help="zh: 为每个分组绘制置信椭圆。\nen: Draw confidence ellipses for each group."
    ),
    ellipse_std: float = typer.Option(
        2.0, help="zh: 置信椭圆的标准差。\nen: Standard deviation for confidence ellipses."
    ),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
) -> None:
    """
    zh: 生成 PCA 图。
    en: Generate PCA plot.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = PCAPlot(theme=theme)
    plotter.plot(
        data=df,
        hue=hue,
        style=style,
        size=size,
        index_col=index_col,
        transpose=transpose,
        title=title,
        cluster=cluster,
        n_clusters=n_clusters,
        add_ellipse=add_ellipse,
        ellipse_std=ellipse_std,
        output=str(output),
    )
    typer.echo(f"Saved PCA plot to {output}")
