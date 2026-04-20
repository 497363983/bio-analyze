from __future__ import annotations

from typing import Any

import pandas as pd

from .. import framework


@framework.register_quantifier
class FeatureCountsQuantifier(framework.BaseQuantifier):
    """Alignment-based gene quantification using featureCounts."""

    TOOL_NAME = "featurecounts"
    MODE = "alignments"
    REQUIRED_BINARIES = ("featureCounts",)
    REQUIRES_READS = False
    REQUIRES_ALIGNMENTS = True
    REQUIRES_GTF = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counts_file = self.output_dir / "featureCounts.txt"

    def execute(self) -> framework.QuantRunResult:
        """Execute featureCounts on all aligned samples."""
        if not self.counts_file.exists():
            framework.logger.info("Running featureCounts quantification...")
            ordered_samples = list(self.alignments)
            cmd = [
                "featureCounts",
                "-T",
                str(self.threads),
                "-a",
                str(self.reference["gtf"]),
                "-o",
                str(self.counts_file),
            ]
            cmd.extend(self.get_template_args("quant"))
            cmd.extend(str(self.alignments[sample]) for sample in ordered_samples)
            framework.run_command(cmd, check=True)

        df = pd.read_csv(self.counts_file, sep="\t", comment="#")
        sample_names = list(self.alignments)
        count_columns = list(df.columns[6 : 6 + len(sample_names)])
        count_matrix = df[count_columns].copy()
        count_matrix.columns = sample_names
        count_matrix.index = df["Geneid"]
        count_matrix = count_matrix.fillna(0).astype(int)
        metrics = {
            "length": pd.DataFrame({"length": df["Length"].values}, index=df["Geneid"]),
        }
        summary = self.counts_file.with_suffix(".txt.summary")
        sample_stats: dict[str, Any] = {}
        if summary.exists():
            summary_df = pd.read_csv(summary, sep="\t", index_col=0)
            sample_stats = {str(key): value for key, value in summary_df.to_dict().items()}
        return framework.QuantRunResult(
            tool=self.TOOL_NAME,
            output_dir=self.output_dir,
            counts_matrix=count_matrix,
            metric_matrices=metrics,
            sample_outputs={sample: self.alignments[sample] for sample in sample_names},
            sample_stats=sample_stats,
        )
