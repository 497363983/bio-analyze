from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option
from bio_analyze_core.i18n import _
from bio_analyze_core.logging import get_logger

from ..plots.tree import TreePlot

logger = get_logger(__name__)

def tree_cmd(
    input_file: Path = Option(
        ...,
        "-i", "--input",
        help=_("Path to the input tree file (Newick format)")
    ),
    output_file: Path = Option(
        ...,
        "-o", "--output",
        help=_("Output image path")
    ),
    format: str = Option(
        "newick",
        "--format",
        help=_("Tree file format (newick/nexus)")
    ),
    layout: str = Option(
        "rectangular",
        "--layout",
        help=_("Tree layout (rectangular/circular)")
    ),
    show_confidence: bool = Option(
        True,
        "--show-confidence/--no-confidence",
        help=_("Whether to show branch support values")
    ),
    theme: str = Option(
        "default",
        "--theme",
        help=_("Plot theme (default/nature/science)")
    ),
    branch_thickness: float = Option(
        1.0,
        "--branch-thickness",
        help=_("Branch line thickness")
    ),
    font_size: int = Option(
        10,
        "--font-size",
        help=_("Font size")
    ),
    label_offset_scale: float = Option(
        0.05,
        "--label-offset-scale",
        help=_("Relative label offset scale")
    ),
    label_bbox_alpha: float = Option(
        0.65,
        "--label-bbox-alpha",
        help=_("Label background alpha (0-1)")
    )
):
    """
    Plot a phylogenetic tree
    """
    logger.info(f"Plotting phylogenetic tree for {input_file}")

    try:
        plotter = TreePlot(theme=theme)
        plotter.plot(
            data=str(input_file),
            output=str(output_file),
            format=format,
            layout=layout,
            show_confidence=show_confidence,
            branch_thickness=branch_thickness,
            font_size=font_size,
            label_offset_scale=label_offset_scale,
            label_bbox_alpha=label_bbox_alpha
        )
        logger.info(f"Tree plot saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to plot tree: {e}")
        raise Exit(1) from e
