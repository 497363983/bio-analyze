from __future__ import annotations

from pathlib import Path

import pandas as pd

from .. import framework


@framework.register_quantifier
class HTSeqCountQuantifier(framework.BaseQuantifier):
    """Alignment-based gene quantification using HTSeq-count."""

    TOOL_NAME = "htseq-count"
    MODE = "alignments"
    REQUIRED_BINARIES = ("htseq-count",)
    REQUIRES_READS = False
    REQUIRES_ALIGNMENTS = True
    REQUIRES_GTF = True

    def quantify_sample(self, sample: str, bam_file: Path) -> Path:
        """Run HTSeq-count for a single aligned sample."""
        output_file = self.output_dir / f"{sample}.counts.tsv"
        if output_file.exists():
            framework.logger.info(f"Sample {sample} already quantified with HTSeq-count.")
            return output_file

        cmd = ["htseq-count", *self.get_template_args("quant"), str(bam_file), str(self.reference["gtf"])]
        result = framework.run_command(cmd, check=True)
        if isinstance(result.stdout, (bytes, bytearray, memoryview)):
            stdout_text = bytes(result.stdout).decode("utf-8", errors="replace")
        else:
            stdout_text = str(result.stdout or "")
        with open(output_file, "w", encoding="utf-8") as handle:
            handle.write(stdout_text)
        return output_file

    def execute(self) -> framework.QuantRunResult:
        """Execute HTSeq-count across all aligned samples."""
        count_files = self.run_per_sample(
            self.alignments,
            lambda sample, bam_file: (sample, self.quantify_sample(sample, bam_file)),
        )
        counts = {}
        for sample, path in count_files.items():
            df = pd.read_csv(path, sep="\t", header=None, names=["feature", sample], index_col=0)
            df = df[~df.index.str.startswith("__")]
            counts[sample] = pd.to_numeric(df[sample], errors="coerce").fillna(0)
        count_matrix = pd.DataFrame(counts).fillna(0).astype(int)
        return framework.QuantRunResult(
            tool=self.TOOL_NAME,
            output_dir=self.output_dir,
            counts_matrix=count_matrix,
            sample_outputs=count_files,
        )
