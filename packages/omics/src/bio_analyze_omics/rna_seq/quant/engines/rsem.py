from __future__ import annotations

from pathlib import Path

import pandas as pd

from .. import framework


@framework.register_quantifier
class RSEMQuantifier(framework.BaseQuantifier):
    """Read-based transcript / gene quantification using RSEM."""

    TOOL_NAME = "rsem"
    MODE = "reads"
    REQUIRED_BINARIES = ("rsem-prepare-reference", "rsem-calculate-expression")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_dir = self.output_dir / "rsem_reference"
        self.reference_prefix = self.reference_dir / "reference"

    def build_reference(self) -> Path:
        """Build or reuse the RSEM reference bundle."""
        if self.reference_dir.exists() and (self.reference_prefix.with_suffix(".grp")).exists():
            framework.logger.info("RSEM reference already exists. Skipping build.")
            return self.reference_prefix

        self.reference_dir.mkdir(parents=True, exist_ok=True)
        transcript_fasta = self.prepare_transcriptome_fasta("transcripts.fa")
        cmd = [
            "rsem-prepare-reference",
            str(transcript_fasta),
            str(self.reference_prefix),
        ]
        cmd.extend(self.get_template_args("index"))
        framework.run_command(cmd, check=True)
        return self.reference_prefix

    def quantify_sample(self, sample: str, files: dict) -> Path:
        """Run RSEM expression quantification for a single sample."""
        sample_dir = self.output_dir / sample
        sample_dir.mkdir(parents=True, exist_ok=True)
        prefix = sample_dir / sample
        genes_result = sample_dir / f"{sample}.genes.results"
        if genes_result.exists():
            framework.logger.info(f"Sample {sample} already quantified with RSEM.")
            return genes_result

        cmd = [
            "rsem-calculate-expression",
            "--num-threads",
            str(self.threads),
        ]
        cmd.extend(self.get_template_args("quant"))
        if "R2" in files:
            cmd.extend(["--paired-end", str(files["R1"]), str(files["R2"])])
        else:
            cmd.append(str(files["R1"]))
        cmd.extend([str(self.reference_prefix), str(prefix)])
        framework.run_command(cmd, check=True)
        return genes_result

    def execute(self) -> framework.QuantRunResult:
        """Execute RSEM quantification for all samples."""
        self.build_reference()
        result_files = self.run_per_sample(
            self.reads,
            lambda sample, files: (sample, self.quantify_sample(sample, files)),
        )
        counts = {}
        tpms = {}
        for sample, path in result_files.items():
            df = pd.read_csv(path, sep="\t", index_col=0)
            counts[sample] = df["expected_count"]
            tpms[sample] = df["TPM"]
        return framework.QuantRunResult(
            tool=self.TOOL_NAME,
            output_dir=self.output_dir,
            counts_matrix=pd.DataFrame(counts).fillna(0.0),
            metric_matrices={"tpm": pd.DataFrame(tpms).fillna(0.0)},
            sample_outputs={sample: path.parent for sample, path in result_files.items()},
        )
