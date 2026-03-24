from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseTreeBuilder(ABC):
    """
    Base class for phylogenetic tree builders.
    """
    
    @abstractmethod
    def build(self, alignment_file: Path, output_file: Path, **kwargs: Any) -> Path:
        """
        Build a phylogenetic tree from an alignment.
        
        Args:
            alignment_file: Path to the MSA file (usually FASTA).
            output_file: Path to save the tree (e.g. Newick format).
            **kwargs: Builder-specific options.
            
        Returns:
            Path to the output tree file.
        """
        pass
