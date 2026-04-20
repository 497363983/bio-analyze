from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.pca import PCAPlot


def pca_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(..., "-o", "--output", help=_("Output file path.")),
    hue: str = Option(None, help=_("Grouping column name (hue).")),
    style: str = Option(None, help=_("Column name for marker style.")),
    size: str = Option(None, help=_("Column name for marker size.")),
    index_col: str = Option(
        None, help=_("Column to use as index (e.g. gene names).")
    ),
    transpose: bool = Option(
        True,
        help=_("Transpose input data (default: True, assumes Genes x Samples)."),
    ),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    title: str = Option(None, help=_("Plot title.")),
    cluster: bool = Option(False, help=_("Perform KMeans clustering.")),
    n_clusters: int = Option(3, help=_("Number of clusters for KMeans.")),
    add_ellipse: bool = Option(
        False, help=_("Draw confidence ellipses for each group.")
    ),
    ellipse_std: float = Option(
        2.0, help=_("Standard deviation for confidence ellipses.")
    ),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
) -> None:
    """
    Generate PCA plot.
    """
    df = read_data(input_file, sheet=sheet)
    plotter = PCAPlot(theme=theme)
    plotter.plot(
        data=df,
        hue=hue,
        style=style,
        size=size,
        index_col=index_col,
        transpose=transpose,
        title=title,
        cluster=cluster,
        n_clusters=n_clusters,
        add_ellipse=add_ellipse,
        ellipse_std=ellipse_std,
        output=str(output),
    )
    echo(f"Saved PCA plot to {output}")
