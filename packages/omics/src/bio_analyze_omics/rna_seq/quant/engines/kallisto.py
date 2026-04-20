from __future__ import annotations

from pathlib import Path

import pandas as pd

from .. import framework


@framework.register_quantifier
class KallistoQuantifier(framework.BaseQuantifier):
    """Read-based transcript quantification using Kallisto."""

    TOOL_NAME = "kallisto"
    MODE = "reads"
    REQUIRED_BINARIES = ("kallisto",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index_path = self.output_dir / "kallisto.idx"

    def build_index(self) -> Path:
        """Build or reuse the Kallisto index file."""
        if self.index_path.exists():
            framework.logger.info("Kallisto index already exists. Skipping build.")
            return self.index_path

        transcript_fasta = self.prepare_transcriptome_fasta("transcripts.fa")
        cmd = ["kallisto", "index", "-i", str(self.index_path), str(transcript_fasta)]
        cmd.extend(self.get_template_args("index"))
        framework.run_command(cmd, check=True)
        return self.index_path

    def quantify_sample(self, sample: str, files: dict) -> Path:
        """Run Kallisto quantification for a single sample."""
        out_dir = self.output_dir / sample
        abundance = out_dir / "abundance.tsv"
        if abundance.exists():
            framework.logger.info(f"Sample {sample} already quantified with Kallisto.")
            return abundance

        cmd = [
            "kallisto",
            "quant",
            "-i",
            str(self.index_path),
            "-o",
            str(out_dir),
            "-t",
            str(self.threads),
        ]
        cmd.extend(self.get_template_args("quant"))
        if "R2" in files:
            cmd.extend([str(files["R1"]), str(files["R2"])])
        else:
            fragment_length = self.get_param("fragment_length")
            fragment_sd = self.get_param("fragment_sd")
            if fragment_length is None or fragment_sd is None:
                raise RuntimeError(
                    "Kallisto single-end quantification requires fragment_length and fragment_sd."
                )
            cmd.extend(["--single", "-l", str(fragment_length), "-s", str(fragment_sd), str(files["R1"])])
        framework.run_command(cmd, check=True)
        return abundance

    def execute(self) -> framework.QuantRunResult:
        """Execute Kallisto quantification for all samples."""
        self.build_index()
        abundance_files = self.run_per_sample(
            self.reads,
            lambda sample, files: (sample, self.quantify_sample(sample, files)),
        )
        counts = {}
        tpms = {}
        lengths = {}
        for sample, path in abundance_files.items():
            df = pd.read_csv(path, sep="\t", index_col=0)
            counts[sample] = df["est_counts"]
            tpms[sample] = df["tpm"]
            lengths[sample] = df["eff_length"]
        return framework.QuantRunResult(
            tool=self.TOOL_NAME,
            output_dir=self.output_dir,
            counts_matrix=pd.DataFrame(counts).fillna(0.0),
            metric_matrices={
                "tpm": pd.DataFrame(tpms).fillna(0.0),
                "effective_length": pd.DataFrame(lengths).fillna(0.0),
            },
            sample_outputs={sample: path.parent for sample, path in abundance_files.items()},
        )
