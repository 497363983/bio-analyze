from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.gsea import GSEAPlot


def gsea_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(..., "-o", "--output", help=_("Output file path.")),
    rank: str = Option("rank", help=_("Column name for rank (x-axis).")),
    score: str = Option(
        "running_es", help=_("Column name for running ES (y-axis).")
    ),
    hit: str = Option(
        "hit", help=_("Column name for hit status (0/1 or boolean).")
    ),
    metric: str = Option(
        None, help=_("Column name for ranking metric (y-axis bottom).")
    ),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    title: str = Option(None, help=_("Plot title.")),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
    color: str = Option("#4DAF4A", help=_("Color for enrichment score line.")),
    hit_color: str = Option("black", help=_("Color for hit lines.")),
    nes: float = Option(None, help=_("Normalized Enrichment Score.")),
    pvalue: float = Option(None, help=_("P-value.")),
    fdr: float = Option(None, help=_("FDR q-value.")),
    show_border: bool = Option(True, help=_("Show top and right borders.")),
) -> None:
    """
    Generate GSEA enrichment plot.
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
    echo(f"Saved GSEA plot to {output}")
