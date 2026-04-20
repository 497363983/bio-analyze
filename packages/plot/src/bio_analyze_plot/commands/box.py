from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_plot.commands.utils import read_data
from bio_analyze_plot.plots.box import BoxPlot


def box_cmd(
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
    significance: list[str] = Option(
        None, help=_("Pairs for significance testing (e.g. 'A,B' 'C,D').")
    ),
    test: str = Option("t-test_ind", help=_("Statistical test method.")),
    text_format: str = Option("star", help=_("Significance annotation format.")),
    add_swarm: bool = Option(False, help=_("Overlay swarmplot points.")),
    swarm_color: str = Option(".25", help=_("Swarmplot point color.")),
    swarm_size: float = Option(3.0, help=_("Swarmplot point size.")),
    sheet: str = Option(None, help=_("Sheet name for Excel files.")),
) -> None:
    """
    Generate box plot.
    """
    df = read_data(input_file, sheet=sheet)

    # 解析显著性对
    sig_pairs = []
    if significance:
        for pair_str in significance:
            parts = pair_str.split(",")
            if len(parts) == 2:
                sig_pairs.append((parts[0].strip(), parts[1].strip()))

    plotter = BoxPlot(theme=theme)
    plotter.plot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        title=title,
        output=str(output),
        significance=sig_pairs if sig_pairs else None,
        test=test,
        text_format=text_format,
        add_swarm=add_swarm,
        swarm_color=swarm_color,
        swarm_size=swarm_size,
    )
    echo(f"Saved box plot to {output}")
