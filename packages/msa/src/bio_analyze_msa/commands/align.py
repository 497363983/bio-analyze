from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option
from bio_analyze_core.i18n import _
from bio_analyze_core.logging import get_logger

from ..aligners import MafftAligner, MuscleAligner, PythonAligner

logger = get_logger(__name__)

def align_cmd(
    input_file: Path = Option(
        ...,
        "-i", "--input",
        help=_("Path to the input unaligned FASTA file")
    ),
    output_file: Path = Option(
        ...,
        "-o", "--output",
        help=_("Path to the output aligned FASTA file")
    ),
    method: str = Option(
        "mafft",
        "--method",
        help=_("Alignment algorithm to use (mafft, muscle, python)")
    )
):
    """
    Run multiple sequence alignment (MSA)
    """
    logger.info(f"Starting alignment using {method}")

    if method.lower() == "mafft":
        aligner = MafftAligner()
    elif method.lower() == "muscle":
        aligner = MuscleAligner()
    elif method.lower() == "python":
        aligner = PythonAligner()
    else:
        logger.error(f"Unknown alignment method: {method}")
        raise Exit(1)

    try:
        aligner.align(input_file, output_file)
        logger.info("Alignment completed successfully.")
    except Exception as e:
        logger.error(f"Alignment failed: {e}")
        raise Exit(1) from e
