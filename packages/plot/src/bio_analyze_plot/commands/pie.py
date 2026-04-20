from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.pie import PiePlot


def pie_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(..., "-o", "--output", help=_("Output file path.")),
    x: str = Option(..., help=_("Column name for labels (categorical).")),
    y: str = Option(..., help=_("Column name for values (numerical).")),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    title: str = Option(None, help=_("Plot title.")),
    autopct: str = Option("%1.1f%%", help=_("Percentage format.")),
    startangle: float = Option(90, help=_("Start angle.")),
    explode: str = Option(
        None,
        help=_("Explode slices. Can be a column name or comma-separated values."),
    ),
    shadow: bool = Option(False, help=_("Show shadow.")),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
) -> None:
    """
    Generate pie chart.
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
                echo(f"Warning: Invalid explode format '{explode}'. Ignored.")

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
    echo(f"Saved pie chart to {output}")
