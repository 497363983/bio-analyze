from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.gsea import GSEAPlot


def gsea_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
    ),
    output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
    rank: str = typer.Option("rank", help="zh: 排名列名 (X 轴)。\nen: Column name for rank (x-axis)."),
    score: str = typer.Option(
        "running_es", help="zh: 运行富集得分列名 (Y 轴)。\nen: Column name for running ES (y-axis)."
    ),
    hit: str = typer.Option(
        "hit", help="zh: 命中状态列名 (0/1 或布尔值)。\nen: Column name for hit status (0/1 or boolean)."
    ),
    metric: str = typer.Option(
        None, help="zh: 排名指标列名 (Y 轴底部)。\nen: Column name for ranking metric (y-axis bottom)."
    ),
    theme: str = typer.Option(
        "nature",
        help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
    ),
    title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    color: str = typer.Option("#4DAF4A", help="zh: 富集得分曲线颜色。\nen: Color for enrichment score line."),
    hit_color: str = typer.Option("black", help="zh: 命中线条颜色。\nen: Color for hit lines."),
    nes: float = typer.Option(None, help="zh: 标准化富集得分 (NES)。\nen: Normalized Enrichment Score."),
    pvalue: float = typer.Option(None, help="zh: P-value。\nen: P-value."),
    fdr: float = typer.Option(None, help="zh: FDR q-value。\nen: FDR q-value."),
    show_border: bool = typer.Option(True, help="zh: 显示顶部和右侧边框。\nen: Show top and right borders."),
) -> None:
    """
    zh: 生成 GSEA 富集图。
    en: Generate GSEA enrichment plot.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = GSEAPlot(theme=theme)
    plotter.plot(
        data=df,
        rank=rank,
        score=score,
        hit=hit,
        metric=metric,
        title=title,
        output=str(output),
        color=color,
        hit_color=hit_color,
        nes=nes,
        pvalue=pvalue,
        fdr=fdr,
        show_border=show_border,
    )
    typer.echo(f"Saved GSEA plot to {output}")
