from pathlib import Path
from typing import Any

from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

from bio_analyze_core.logging import get_logger

from .base import BaseTreeBuilder

logger = get_logger(__name__)


class DistanceTreeBuilder(BaseTreeBuilder):
    """
    Pure Python distance-based tree builder using Biopython.
    Supports UPGMA and Neighbor-Joining (NJ).
    """

    def build(self, alignment_file: Path, output_file: Path, **kwargs: Any) -> Path:
        """
        Build distance tree.
        
        Args:
            alignment_file: MSA file in FASTA format.
            output_file: Output Newick file.
            **kwargs:
                method (str): 'nj' or 'upgma'. Default 'nj'.
                model (str): Distance model, e.g., 'identity', 'blosum62'. Default 'identity'.
        """
        method = kwargs.get("method", "nj").lower()
        if method not in ["nj", "upgma"]:
            raise ValueError(f"Unsupported method '{method}'. Use 'nj' or 'upgma'.")
            
        model = kwargs.get("model", "identity")
        
        logger.info(f"Reading alignment from {alignment_file}")
        alignment = AlignIO.read(alignment_file, "fasta")
        
        logger.info(f"Calculating distance matrix using model '{model}'")
        calculator = DistanceCalculator(model)
        dm = calculator.get_distance(alignment)
        
        logger.info(f"Building {method.upper()} tree")
        constructor = DistanceTreeConstructor()
        if method == "nj":
            tree = constructor.nj(dm)
        else:
            tree = constructor.upgma(dm)
            
        logger.info(f"Saving tree to {output_file}")
        Phylo.write(tree, output_file, "newick")
        
        return output_file
