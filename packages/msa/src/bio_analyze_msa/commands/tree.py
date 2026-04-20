from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option
from bio_analyze_core.i18n import _
from bio_analyze_core.logging import get_logger

from ..tree import DistanceTreeBuilder, FastTreeBuilder

logger = get_logger(__name__)

def tree_cmd(
    input_file: Path = Option(
        ...,
        "-i", "--input",
        help=_("Path to the input MSA file")
    ),
    output_file: Path = Option(
        ...,
        "-o", "--output",
        help=_("Path to the output phylogenetic tree file (Newick format)")
    ),
    method: str = Option(
        "nj",
        "--method",
        help=_("Tree building algorithm (nj, upgma, fasttree)")
    )
):
    """
    Build a phylogenetic tree from an MSA
    """
    logger.info(f"Starting tree building using {method}")

    try:
        if method.lower() in ["nj", "upgma"]:
            builder = DistanceTreeBuilder()
            builder.build(input_file, output_file, method=method.lower())
        elif method.lower() == "fasttree":
            builder = FastTreeBuilder()
            builder.build(input_file, output_file)
        else:
            logger.error(f"Unknown tree building method: {method}")
            raise Exit(1)

        logger.info("Tree building completed successfully.")
    except Exception as e:
        logger.error(f"Tree building failed: {e}")
        raise Exit(1) from e
