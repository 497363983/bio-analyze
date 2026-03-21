from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.bar import BarPlot


def bar_cmd(
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
    error_bar_type: str = typer.Option(None, help="zh: 误差棒类型: SD, SE, CI。\nen: Error bar type: SD, SE, CI."),
    error_bar_ci: float = typer.Option(
        95, help="zh: 置信区间大小 (默认: 95)。\nen: Confidence interval size (default: 95)."
    ),
    error_bar_max: str = typer.Option(
        None, help="zh: 误差棒上限列名。\nen: Column name for error bar upper limit."
    ),
    error_bar_min: str = typer.Option(
        None, help="zh: 误差棒下限列名。\nen: Column name for error bar lower limit."
    ),
    error_bar_capsize: float = typer.Option(0.1, help="zh: 误差棒帽大小。\nen: Error bar capsize."),
    significance: list[str] = typer.Option(
        None, help="zh: 显著性检验配对 (例如 'A,B' 'C,D')。\nen: Pairs for significance testing (e.g. 'A,B' 'C,D')."
    ),
    test: str = typer.Option("t-test_ind", help="zh: 统计检验方法。\nen: Statistical test method."),
    text_format: str = typer.Option("star", help="zh: 显著性标注格式。\nen: Significance annotation format."),
    sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
) -> None:
    """
    zh: 生成柱状图。
    en: Generate bar plot.
    """
    df = read_data(input_file, sheet=sheet)

    # 解析显著性对
    sig_pairs = []
    if significance:
        for pair_str in significance:
            parts = pair_str.split(",")
            if len(parts) == 2:
                sig_pairs.append((parts[0].strip(), parts[1].strip()))

    plotter = BarPlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        title=title,
        output=str(output),
        error_bar_type=error_bar_type,
        error_bar_ci=error_bar_ci,
        error_bar_max=error_bar_max,
        error_bar_min=error_bar_min,
        error_bar_capsize=error_bar_capsize,
        significance=sig_pairs if sig_pairs else None,
        test=test,
        text_format=text_format,
    )
    typer.echo(f"Saved bar plot to {output}")
