from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.bar import BarPlot


def bar_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(..., "-o", "--output", help=_("Output file path.")),
    x: str = Option(..., help=_("Column name for X-axis.")),
    y: str = Option(..., help=_("Column name for Y-axis.")),
    hue: str = Option(None, help=_("Grouping column name (hue).")),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    title: str = Option(None, help=_("Plot title.")),
    error_bar_type: str = Option(None, help=_("Error bar type: SD, SE, CI.")),
    error_bar_ci: float = Option(
        95, help=_("Confidence interval size (default: 95).")
    ),
    error_bar_max: str = Option(
        None, help=_("Column name for error bar upper limit.")
    ),
    error_bar_min: str = Option(
        None, help=_("Column name for error bar lower limit.")
    ),
    error_bar_capsize: float = Option(0.1, help=_("Error bar capsize.")),
    significance: list[str] = Option(
        None, help=_("Pairs for significance testing (e.g. 'A,B' 'C,D').")
    ),
    test: str = Option("t-test_ind", help=_("Statistical test method.")),
    text_format: str = Option("star", help=_("Significance annotation format.")),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
) -> None:
    """
    Generate bar plot.
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
    echo(f"Saved bar plot to {output}")
