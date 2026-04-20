import json
from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option
from bio_analyze_core.i18n import _
from bio_analyze_core.logging import get_logger

from ..plots.msa import MsaPlot

logger = get_logger(__name__)

def msa_cmd(
    input_file: Path = Option(
        ...,
        "-i", "--input",
        help=_("Path to the input MSA file (FASTA)")
    ),
    output_file: Path = Option(
        ...,
        "-o", "--output",
        help=_("Output image path")
    ),
    seq_type: str = Option(
        "aa",
        "--seq-type",
        help=_("Sequence type (aa/nt)")
    ),
    show_logo: bool = Option(
        True,
        "--show-logo/--no-logo",
        help=_("Whether to show a conservation logo at the top")
    ),
    theme: str = Option(
        "default",
        "--theme",
        help=_("Plot theme (default/nature/science)")
    ),
    font_size: int = Option(
        10,
        "--font-size",
        help=_("Font size")
    ),
    bases_per_line: int = Option(
        0,
        "--bases-per-line",
        help=_("Residues per line for wrapping, 0 means no wrap")
    ),
    base_colors: str | None = Option(
        None,
        "--base-colors",
        help=_("JSON mapping for custom residue colors, e.g. '{\"A\":\"#000000\"}'")
    )
):
    """
    Plot a Multiple Sequence Alignment (MSA)
    """
    logger.info(f"Plotting MSA for {input_file}")

    try:
        parsed_base_colors: dict[str, str] | None = None
        if base_colors:
            parsed_base_colors = json.loads(base_colors)
            if not isinstance(parsed_base_colors, dict):
                raise ValueError("base_colors must be a JSON object mapping bases to colors")
        plotter = MsaPlot(theme=theme)
        if bases_per_line > 0 and parsed_base_colors is not None:
            plotter.plot(
                data=str(input_file),
                output=str(output_file),
                seq_type=seq_type,
                show_logo=show_logo,
                font_size=font_size,
                bases_per_line=bases_per_line,
                base_colors=parsed_base_colors,
            )
        elif bases_per_line > 0:
            plotter.plot(
                data=str(input_file),
                output=str(output_file),
                seq_type=seq_type,
                show_logo=show_logo,
                font_size=font_size,
                bases_per_line=bases_per_line,
            )
        elif parsed_base_colors is not None:
            plotter.plot(
                data=str(input_file),
                output=str(output_file),
                seq_type=seq_type,
                show_logo=show_logo,
                font_size=font_size,
                base_colors=parsed_base_colors,
            )
        else:
            plotter.plot(
                data=str(input_file),
                output=str(output_file),
                seq_type=seq_type,
                show_logo=show_logo,
                font_size=font_size,
            )
        logger.info(f"MSA plot saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to plot MSA: {e}")
        raise Exit(1) from e
