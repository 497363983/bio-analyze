from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.heatmap import HeatmapPlot


def heatmap_cmd(
    input_file: Path = Argument(
        ..., help=_("Input file path (CSV, TSV, or Excel).")
    ),
    output: Path = Option(..., "-o", "--output", help=_("Output file path.")),
    index_col: str = Option(None, help=_("Column to use as row index.")),
    cluster_rows: bool = Option(True, help=_("Whether to cluster rows.")),
    cluster_cols: bool = Option(True, help=_("Whether to cluster columns.")),
    z_score: int = Option(
        None,
        help=_("0 (rows) or 1 (columns) for standardization. None to disable."),
    ),
    cmap: str = Option(
        None, help=_("Colormap name (e.g. 'vlag', 'coolwarm').")
    ),
    center: float = Option(None, help=_("Value at which to center the colormap.")),
    theme: str = Option(
        "nature",
        help=_("Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
    ),
    title: str = Option(None, help=_("Plot title.")),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
) -> None:
    """
    Generate heatmap/clustermap.
    """
    df = read_data(input_file, sheet=sheet)

    # 准备传递给 plot 的 kwargs，过滤掉 None 的值以允许使用默认值/主题值
    kwargs = {}
    if cmap is not None:
        kwargs["cmap"] = cmap
    if center is not None:
        kwargs["center"] = center

    plotter = HeatmapPlot(theme=theme)
    plotter.plot(
        data=df,
        index_col=index_col,
        cluster_rows=cluster_rows,
        cluster_cols=cluster_cols,
        z_score=z_score,
        title=title,
        output=str(output),
        **kwargs,
    )
    echo(f"Saved heatmap to {output}")
