import shutil
from pathlib import Path
from typing import Any

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run

from .base import BaseTreeBuilder

logger = get_logger(__name__)


class FastTreeBuilder(BaseTreeBuilder):
    """
    Maximum Likelihood tree builder using FastTree.
    Requires 'FastTree' to be available in the system PATH.
    """

    def __init__(self, executable: str = "FastTree"):
        self.executable = executable
        if not shutil.which(self.executable):
            logger.warning(f"FastTree executable '{self.executable}' not found in PATH.")

    def build(self, alignment_file: Path, output_file: Path, **kwargs: Any) -> Path:
        """
        Build ML tree using FastTree.
        
        Args:
            alignment_file: MSA file in FASTA format.
            output_file: Output Newick file.
            **kwargs: Extra flags to pass to FastTree.
                nt (bool): If True, use nucleotide model (-nt).
        """
        if not shutil.which(self.executable):
            raise FileNotFoundError(
                f"FastTree executable '{self.executable}' not found. "
                "Please install FastTree or use distance-based methods."
            )

        args = [self.executable]
        
        # Add flags
        for k, v in kwargs.items():
            if isinstance(v, bool):
                if v:
                    args.append(f"-{k}")
            else:
                args.extend([f"-{k}", str(v)])
                
        # FastTree requires the alignment file as the last argument
        args.append(str(alignment_file))
        
        logger.info(f"Running FastTree on {alignment_file}")
        
        # FastTree writes the tree to stdout and logs to stderr
        res = run(args, capture_output=True, text=True, check=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(res.stdout)
            
        logger.info(f"FastTree tree saved to {output_file}")
        return output_file
