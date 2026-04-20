import shutil
from pathlib import Path
from typing import Any

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run

from .base import BaseAligner

logger = get_logger(__name__)


class MafftAligner(BaseAligner):
    """
    Wrapper for the MAFFT alignment tool.
    Requires 'mafft' to be available in the system PATH.
    """

    def __init__(self, executable: str = "mafft"):
        self.executable = executable
        if not shutil.which(self.executable):
            logger.warning(f"MAFFT executable '{self.executable}' not found in PATH.")

    def align(self, input_file: Path, output_file: Path, **kwargs: Any) -> Path:
        """
        Run MAFFT on the input file.

        Args:
            input_file: Path to unaligned sequences (FASTA).
            output_file: Path to save aligned sequences.
            **kwargs: Extra flags to pass to mafft. For example, auto=True adds '--auto'.
        """
        if not shutil.which(self.executable):
            raise FileNotFoundError(
                f"MAFFT executable '{self.executable}' not found. "
                "Please install MAFFT or use another aligner."
            )

        args = [self.executable]

        # Default to auto if no specific algorithm is requested
        if "auto" not in kwargs and not any(k in kwargs for k in ["localpair", "globalpair", "genafpair"]):
            kwargs["auto"] = True

        for k, v in kwargs.items():
            if isinstance(v, bool):
                if v:
                    args.append(f"--{k}")
            else:
                args.extend([f"--{k}", str(v)])

        args.append(str(input_file))

        logger.info(f"Running MAFFT on {input_file}")

        # MAFFT outputs alignment to stdout
        res = run(args, capture_output=True, text=True, check=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(res.stdout)

        logger.info(f"MAFFT alignment saved to {output_file}")
        return output_file
