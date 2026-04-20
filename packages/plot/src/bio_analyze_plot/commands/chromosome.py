from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.chromosome import ChromosomePlot


def chromosome_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(..., "-o", "--output", help=_("Output file path.")),
    chrom_col: str = Option("chrom", help=_("Column name for chromosome.")),
    pos_col: str = Option("pos", help=_("Column name for position.")),
    pos_counts_col: str = Option(
        "pos_counts", help=_("Column name for positive strand counts.")
    ),
    neg_counts_col: str = Option(
        "neg_counts", help=_("Column name for negative strand counts.")
    ),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    title: str = Option(None, help=_("Plot title.")),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
    max_chroms: int = Option(
        24, help=_("Maximum number of chromosomes to display.")
    ),
) -> None:
    """
    Generate chromosome coverage distribution plot.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = ChromosomePlot(theme=theme)
    plotter.plot(
        data=df,
        chrom_col=chrom_col,
        pos_col=pos_col,
        pos_counts_col=pos_counts_col,
        neg_counts_col=neg_counts_col,
        max_chroms=max_chroms,
        title=title,
        output=str(output),
    )
    echo(f"Saved chromosome plot to {output}")
