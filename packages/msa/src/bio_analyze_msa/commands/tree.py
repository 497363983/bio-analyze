from pathlib import Path
import typer

from bio_analyze_core.logging import get_logger
from ..tree import DistanceTreeBuilder, FastTreeBuilder

logger = get_logger(__name__)

def tree_cmd(
    input_file: Path = typer.Option(
        ...,
        "-i", "--input",
        help="zh: 输入的多序列比对(MSA)文件路径\nen: Path to the input MSA file"
    ),
    output_file: Path = typer.Option(
        ...,
        "-o", "--output",
        help="zh: 输出的系统发育树文件路径(Newick格式)\nen: Path to the output phylogenetic tree file (Newick format)"
    ),
    method: str = typer.Option(
        "nj",
        "--method",
        help="zh: 建树算法 (nj, upgma, fasttree)\nen: Tree building algorithm (nj, upgma, fasttree)"
    )
):
    """
    zh: 根据多序列比对结果构建系统发育树
    en: Build a phylogenetic tree from an MSA
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
            raise typer.Exit(1)
            
        logger.info("Tree building completed successfully.")
    except Exception as e:
        logger.error(f"Tree building failed: {e}")
        raise typer.Exit(1)
