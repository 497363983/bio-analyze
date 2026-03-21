from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.box import BoxPlot


def box_cmd(
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
    significance: list[str] = typer.Option(
        None, help="zh: 显著性检验配对 (例如 'A,B' 'C,D')。\nen: Pairs for significance testing (e.g. 'A,B' 'C,D')."
    ),
    test: str = typer.Option("t-test_ind", help="zh: 统计检验方法。\nen: Statistical test method."),
    text_format: str = typer.Option("star", help="zh: 显著性标注格式。\nen: Significance annotation format."),
    add_swarm: bool = typer.Option(False, help="zh: 叠加蜂群图点。\nen: Overlay swarmplot points."),
    swarm_color: str = typer.Option(".25", help="zh: 蜂群图点颜色。\nen: Swarmplot point color."),
    swarm_size: float = typer.Option(3.0, help="zh: 蜂群图点大小。\nen: Swarmplot point size."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
) -> None:
    """
    zh: 生成箱线图。
    en: Generate box plot.
    """
    df = read_data(input_file, sheet=sheet)

    # 解析显著性对
    sig_pairs = []
    if significance:
        for pair_str in significance:
            parts = pair_str.split(",")
            if len(parts) == 2:
                sig_pairs.append((parts[0].strip(), parts[1].strip()))

    plotter = BoxPlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        title=title,
        output=str(output),
        significance=sig_pairs if sig_pairs else None,
        test=test,
        text_format=text_format,
        add_swarm=add_swarm,
        swarm_color=swarm_color,
        swarm_size=swarm_size,
    )
    typer.echo(f"Saved box plot to {output}")
