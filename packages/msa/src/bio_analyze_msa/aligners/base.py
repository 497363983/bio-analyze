from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseAligner(ABC):
    """
    Base class for all Multiple Sequence Alignment tools.
    """
    
    @abstractmethod
    def align(self, input_file: Path, output_file: Path, **kwargs: Any) -> Path:
        """
        Run the alignment algorithm.
        
        Args:
            input_file: Path to the input unaligned FASTA file.
            output_file: Path to the output aligned file (e.g. FASTA format).
            **kwargs: Additional algorithm-specific arguments.
            
        Returns:
            Path to the output aligned file.
        """
        pass
