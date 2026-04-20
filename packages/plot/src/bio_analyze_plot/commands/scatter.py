from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.scatter import ScatterPlot


def scatter_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(..., "-o", "--output", help=_("Output file path.")),
    x: str = Option(..., help=_("Column name for X-axis.")),
    y: str = Option(..., help=_("Column name for Y-axis.")),
    hue: str = Option(None, help=_("Grouping column name (hue).")),
    style: str = Option(None, help=_("Column name for marker style.")),
    size: str = Option(None, help=_("Column name for marker size.")),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    title: str = Option(None, help=_("Plot title.")),
    add_ellipse: bool = Option(
        False, help=_("Draw confidence ellipses for each group.")
    ),
    ellipse_std: float = Option(
        2.0, help=_("Standard deviation for confidence ellipses.")
    ),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
) -> None:
    """
    Generate scatter plot.
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
    echo(f"Saved scatter plot to {output}")
