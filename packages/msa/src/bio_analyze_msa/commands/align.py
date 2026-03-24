from pathlib import Path
import typer

from bio_analyze_core.logging import get_logger
from ..aligners import MafftAligner, MuscleAligner, PythonAligner

logger = get_logger(__name__)

def align_cmd(
    input_file: Path = typer.Option(
        ...,
        "-i", "--input",
        help="zh: 输入的未比对FASTA文件路径\nen: Path to the input unaligned FASTA file"
    ),
    output_file: Path = typer.Option(
        ...,
        "-o", "--output",
        help="zh: 输出的比对结果FASTA文件路径\nen: Path to the output aligned FASTA file"
    ),
    method: str = typer.Option(
        "mafft",
        "--method",
        help="zh: 使用的比对算法 (mafft, muscle, python)\nen: Alignment algorithm to use (mafft, muscle, python)"
    )
):
    """
    zh: 运行多序列比对(MSA)
    en: Run multiple sequence alignment (MSA)
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
        raise typer.Exit(1)
        
    try:
        aligner.align(input_file, output_file)
        logger.info("Alignment completed successfully.")
    except Exception as e:
        logger.error(f"Alignment failed: {e}")
        raise typer.Exit(1)
