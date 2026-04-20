from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from .. import framework


@framework.register_quantifier
class SalmonQuantifier(framework.BaseQuantifier):
    """Read-based transcript quantification using Salmon."""

    TOOL_NAME = "salmon"
    MODE = "reads"
    REQUIRED_BINARIES = ("salmon",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index_dir = self.output_dir / "salmon_index"

    def is_index_complete(self) -> bool:
        """Check whether the Salmon index exists and contains its manifest."""
        return self.index_dir.exists() and (self.index_dir / "versionInfo.json").exists()

    def cleanup_incomplete_index(self) -> None:
        """Remove a partially built Salmon index directory."""
        if self.index_dir.exists():
            shutil.rmtree(self.index_dir, ignore_errors=True)

    def build_index(self) -> Path:
        """Build or reuse the Salmon index directory."""
        if self.is_index_complete():
            framework.logger.info("Salmon index already exists. Skipping build.")
            return self.index_dir
        if self.index_dir.exists():
            framework.logger.warning("Incomplete Salmon index detected. Rebuilding index from scratch.")
            self.cleanup_incomplete_index()

        transcript_fasta = self.prepare_transcriptome_fasta("transcripts.fa")
        framework.logger.info("Building Salmon index...")
        cmd = [
            "salmon",
            "index",
            "-t",
            str(transcript_fasta),
            "-i",
            str(self.index_dir),
            "-p",
            str(self.threads),
        ]
        cmd.extend(self.get_template_args("index"))
        framework.run_command(cmd, check=True)
        return self.index_dir

    def quantify_sample(self, sample: str, files: dict) -> Path:
        """Run Salmon quantification for a single sample."""
        out_dir = self.output_dir / sample
        quant_file = out_dir / "quant.sf"
        if quant_file.exists():
            framework.logger.info(f"Sample {sample} already quantified with Salmon.")
            return quant_file

        cmd = [
            "salmon",
            "quant",
            "-i",
            str(self.index_dir),
            "-l",
            self.get_param("library_type", "A"),
            "-o",
            str(out_dir),
            "-p",
            str(self.threads),
        ]
        cmd.extend(self.get_template_args("quant"))
        if "R2" in files:
            cmd.extend(["-1", str(files["R1"]), "-2", str(files["R2"])])
        else:
            cmd.extend(["-r", str(files["R1"])])
        framework.run_command(cmd, check=True)
        return quant_file

    def merge_quantifications(self, quant_files: dict[str, Path]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
        """Merge per-sample Salmon outputs into standardized matrices."""
        counts = {}
        tpms = {}
        lengths = {}
        for sample, path in quant_files.items():
            df = pd.read_csv(path, sep="\t", index_col=0)
            counts[sample] = df["NumReads"]
            tpms[sample] = df["TPM"]
            lengths[sample] = df["Length"]
        count_matrix = pd.DataFrame(counts).fillna(0).astype(int)
        tpm_matrix = pd.DataFrame(tpms).fillna(0.0)
        length_matrix = pd.DataFrame(lengths).fillna(0.0)
        return count_matrix, {"tpm": tpm_matrix, "length": length_matrix}

    def collect_stats(self) -> dict[str, Any]:
        """Collect per-sample mapping statistics from Salmon metadata."""
        stats = {}
        for sample_dir in self.output_dir.iterdir():
            meta = sample_dir / "aux_info" / "meta_info.json"
            if sample_dir.is_dir() and meta.exists():
                try:
                    with open(meta, encoding="utf-8") as handle:
                        data = json.load(handle)
                    stats[sample_dir.name] = {
                        "percent_mapped": data.get("percent_mapped", 0.0),
                        "num_processed": data.get("num_processed", 0),
                    }
                except (OSError, json.JSONDecodeError) as exc:
                    framework.logger.warning(f"Failed to parse Salmon stats for {sample_dir.name}: {exc}")
        return stats

    def execute(self) -> framework.QuantRunResult:
        """Execute Salmon quantification for all samples."""
        self.build_index()
        quant_files = self.run_per_sample(
            self.reads,
            lambda sample, files: (sample, self.quantify_sample(sample, files)),
        )
        counts, metrics = self.merge_quantifications(quant_files)
        return framework.QuantRunResult(
            tool=self.TOOL_NAME,
            output_dir=self.output_dir,
            counts_matrix=counts,
            metric_matrices=metrics,
            sample_outputs={sample: path.parent for sample, path in quant_files.items()},
            sample_stats=self.collect_stats(),
        )
