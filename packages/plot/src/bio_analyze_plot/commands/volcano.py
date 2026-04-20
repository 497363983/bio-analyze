from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.volcano import VolcanoPlot


def volcano_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(
        ...,
        "-o",
        "--output",
        help=_("Output file path (e.g. volcano.png)."),
    ),
    x: str = Option(
        "log2FoldChange", help=_("Column name for log2 fold change.")
    ),
    y: str = Option("pvalue", help=_("Column name for p-value.")),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    fc_cutoff: float = Option(1.0, help=_("Fold change cutoff.")),
    p_cutoff: float = Option(0.05, help=_("P-value cutoff.")),
    title: str = Option(None, help=_("Plot title.")),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
) -> None:
    """
    Generate volcano plot from data.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = VolcanoPlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        fc_cutoff=fc_cutoff,
        p_cutoff=p_cutoff,
        title=title,
        output=str(output),
    )
    echo(f"Saved volcano plot to {output}")
