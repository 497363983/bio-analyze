import shutil
from pathlib import Path
from typing import Any

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run

from .base import BaseAligner

logger = get_logger(__name__)


class MuscleAligner(BaseAligner):
    """
    Wrapper for the MUSCLE alignment tool.
    Supports MUSCLE v5 (uses -align) and MUSCLE v3 (uses -in).
    Requires 'muscle' to be available in the system PATH.
    """

    def __init__(self, executable: str = "muscle"):
        self.executable = executable
        if not shutil.which(self.executable):
            logger.warning(f"MUSCLE executable '{self.executable}' not found in PATH.")

    def align(self, input_file: Path, output_file: Path, **kwargs: Any) -> Path:
        """
        Run MUSCLE on the input file.

        Args:
            input_file: Path to unaligned sequences (FASTA).
            output_file: Path to save aligned sequences.
            **kwargs: Extra flags to pass to muscle.
        """
        if not shutil.which(self.executable):
            raise FileNotFoundError(
                f"MUSCLE executable '{self.executable}' not found. "
                "Please install MUSCLE or use another aligner."
            )

        # Check MUSCLE version to determine arguments
        res = run([self.executable, "-version"], capture_output=True, text=True, check=False)
        output = res.stdout + res.stderr

        is_v5 = "MUSCLE v5" in output or "MUSCLE 5" in output

        if is_v5:
            args = [self.executable, "-align", str(input_file), "-output", str(output_file)]
        else:
            args = [self.executable, "-in", str(input_file), "-out", str(output_file)]

        for k, v in kwargs.items():
            if isinstance(v, bool):
                if v:
                    args.append(f"-{k}")
            else:
                args.extend([f"-{k}", str(v)])

        logger.info(f"Running MUSCLE on {input_file}")
        run(args, capture_output=True, text=True, check=True)

        logger.info(f"MUSCLE alignment saved to {output_file}")
        return output_file
