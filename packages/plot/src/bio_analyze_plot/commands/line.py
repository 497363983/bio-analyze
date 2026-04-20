from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.line import LinePlot


def line_cmd(
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
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
    error_bar_type: str = Option(None, help=_("Error bar type: SD, SE, CI.")),
    error_bar_ci: float = Option(
        95, help=_("Confidence interval size (default: 95).")
    ),
    error_bar_capsize: float = Option(
        3.0, help=_("Error bar capsize (in points).")
    ),
    markers: bool = Option(
        False, help=_("Use default markers for data points.")
    ),
    marker_style: str = Option(
        None,
        help=_("Specific marker symbols (comma-separated, e.g. 'o,s'). Overrides --markers."),
    ),
    dashes: bool = Option(True, help=_("Use dashes for lines.")),
    smooth: bool = Option(False, help=_("Enable smooth curve fitting.")),
    smooth_points: int = Option(300, help=_("Number of points for interpolation.")),
) -> None:
    """
    Generate line plot.
    """
    df = read_data(input_file, sheet=sheet)

    # Parse markers
    markers_arg = markers
    if marker_style:
        markers_arg = [m.strip() for m in marker_style.split(",")] if "," in marker_style else marker_style

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
    echo(f"Saved line plot to {output}")
