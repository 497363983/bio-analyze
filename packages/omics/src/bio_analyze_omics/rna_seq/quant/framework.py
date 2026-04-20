"""Plugin-based quantification framework built on the shared core engine runtime."""

from __future__ import annotations


import gzip
import json
import shutil
from abc import ABC
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pandas as pd

from bio_analyze_core.engine import (
    BaseEngine,
    EngineConfig,
    EngineContext,
    EngineManager,
    EngineRegistry,
    EngineSpec,
)
from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run as run_command

logger = get_logger(__name__)

DEFAULT_QUANT_TOOL = "salmon"
DEFAULT_PARAMETER_TEMPLATES: dict[str, dict[str, dict[str, list[str]]]] = {
    "salmon": {
        "default": {"index": [], "quant": ["--validateMappings"]},
        "fast": {"index": [], "quant": []},
    },
    "kallisto": {
        "default": {"index": [], "quant": []},
        "bootstrap": {"index": [], "quant": ["-b", "100"]},
    },
    "featurecounts": {
        "default": {"quant": ["-t", "exon", "-g", "gene_id"]},
        "fractional": {"quant": ["-t", "exon", "-g", "gene_id", "--fraction"]},
    },
    "htseq-count": {
        "default": {"quant": ["-f", "bam", "-r", "pos", "-s", "no", "-i", "gene_id"]},
    },
    "rsem": {
        "default": {"index": [], "quant": []},
    },
}


@dataclass
class QuantToolSpec:
    """Static metadata describing a quantification backend."""
    name: str
    mode: str
    required_binaries: tuple[str, ...]
    description: str


@dataclass
class QuantRunResult:
    """Normalized quantification outputs produced by a backend run."""
    tool: str
    output_dir: Path
    counts_matrix: pd.DataFrame
    metric_matrices: dict[str, pd.DataFrame] = field(default_factory=dict)
    sample_outputs: dict[str, Path] = field(default_factory=dict)
    sample_stats: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def write_standard_outputs(self) -> None:
        """Write standardized count matrices, metrics, and manifests to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.counts_matrix.to_csv(self.output_dir / "counts.csv")
        for metric_name, matrix in self.metric_matrices.items():
            matrix.to_csv(self.output_dir / f"{metric_name}.csv")

        manifest = {
            "tool": self.tool,
            "sample_outputs": {sample: str(path) for sample, path in self.sample_outputs.items()},
            "sample_stats": self.sample_stats,
            "metadata": self.metadata,
            "metrics": sorted(self.metric_matrices),
        }
        with open(self.output_dir / "result_manifest.json", "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=2)


class QuantifierRegistry:
    """Compatibility facade that proxies quant backends into ``EngineRegistry``."""
    @classmethod
    def register(cls, quantifier_cls: type["BaseQuantifier"]) -> type["BaseQuantifier"]:
        """Register a quantifier class in the shared engine registry."""
        return cast(
            type[BaseQuantifier],
            EngineRegistry.register(quantifier_cls.engine_spec(), quantifier_cls),
        )

    @classmethod
    def get(cls, tool_name: str) -> type["BaseQuantifier"]:
        """Return a quantifier class by tool name."""
        return cast(type[BaseQuantifier], EngineRegistry.get("quant", tool_name))

    @classmethod
    def names(cls) -> list[str]:
        """List available quantifier names."""
        return [spec.name for spec in EngineRegistry.list(domain="quant")]

    @classmethod
    def specs(cls) -> dict[str, QuantToolSpec]:
        """Return normalized specs for all registered quantifiers."""
        return {
            spec.name: QuantToolSpec(
                name=spec.name,
                mode=getattr(cls.get(spec.name), "MODE", "reads"),
                required_binaries=spec.required_binaries,
                description=spec.description,
            )
            for spec in EngineRegistry.list(domain="quant")
        }


class BaseQuantifier(BaseEngine, ABC):
    """Domain-specific base class for quantification engines."""
    TOOL_NAME = "base"
    MODE = "reads"
    REQUIRED_BINARIES: tuple[str, ...] = ()
    REQUIRES_READS = True
    REQUIRES_ALIGNMENTS = False
    REQUIRES_GTF = False

    def __init__(
        self,
        reads: dict[str, dict] | None,
        reference: dict[str, Path | str | None],
        output_dir: Path,
        threads: int = 4,
        alignments: dict[str, Path] | None = None,
        tool_config: dict[str, Any] | None = None,
        context: EngineContext | None = None,
        config: EngineConfig | dict[str, Any] | None = None,
    ):
        context = context or EngineContext(output_dir=output_dir, threads=threads, logger=logger)
        config = EngineConfig.from_value(config or tool_config or {})
        self.reads = reads or {}
        self.reference = reference or {}
        self.output_dir = output_dir
        self.threads = threads
        self.alignments = alignments or {}
        self.tool_config = tool_config or {}
        self.output_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(context=context, config=config)

    @classmethod
    def spec(cls) -> QuantToolSpec:
        """Return the compatibility-layer quantifier spec."""
        return QuantToolSpec(
            name=cls.TOOL_NAME,
            mode=cls.MODE,
            required_binaries=cls.REQUIRED_BINARIES,
            description=(cls.__doc__ or "").strip(),
        )

    @classmethod
    def engine_spec(cls) -> EngineSpec:
        """Return the shared engine spec for registry and entry-point use."""
        return EngineSpec(
            domain="quant",
            name=cls.TOOL_NAME,
            version="1",
            description=(cls.__doc__ or "").strip(),
            capabilities=(cls.MODE,),
            required_binaries=cls.REQUIRED_BINARIES,
        )

    def run(self) -> QuantRunResult:
        """Run the quantifier and persist standardized outputs."""
        result = super().run()
        result.metadata.setdefault("tool", self.TOOL_NAME)
        result.metadata.setdefault("mode", self.MODE)
        result.metadata.setdefault("required_binaries", list(self.REQUIRED_BINARIES))
        result.metadata.setdefault("tool_config", self.tool_config)
        result.write_standard_outputs()
        return result

    def validate_inputs(self) -> None:
        """Validate reads, alignments, and reference requirements."""
        if self.REQUIRES_READS and not self.reads:
            raise RuntimeError(f"Quantifier '{self.TOOL_NAME}' requires clean reads.")
        if self.REQUIRES_ALIGNMENTS and not self.alignments:
            raise RuntimeError(f"Quantifier '{self.TOOL_NAME}' requires alignment BAM files.")
        if not self.reference.get("fasta"):
            raise RuntimeError(
                f"Reference FASTA is required for quantifier '{self.TOOL_NAME}'."
            )
        if self.REQUIRES_GTF and not self.reference.get("gtf"):
            raise RuntimeError(
                f"Reference GTF is required for quantifier '{self.TOOL_NAME}'."
            )

    def get_template_args(self, phase: str) -> list[str]:
        """Resolve templated command-line arguments for a specific phase."""
        template_name = self.tool_config.get("template", "default")
        tool_templates = DEFAULT_PARAMETER_TEMPLATES.get(self.TOOL_NAME, {})
        template_args = list(tool_templates.get(template_name, {}).get(phase, []))
        phase_args = self.tool_config.get("phases", {}).get(phase, [])
        if isinstance(phase_args, str):
            template_args.extend(phase_args.split())
        else:
            template_args.extend(str(item) for item in phase_args)
        return template_args

    def get_param(self, name: str, default: Any = None) -> Any:
        """Read a single structured tool parameter with a default fallback."""
        return self.tool_config.get("params", {}).get(name, default)

    def get_sample_workers(self) -> int:
        """Return the configured sample-level worker count."""
        workers = int(self.tool_config.get("sample_workers", 1))
        return max(1, workers)

    def prepare_gtf(self, gtf: Path) -> Path:
        """Prepare an annotation file, decompressing ``.gz`` files when required."""
        if gtf.suffix != ".gz":
            return gtf

        prepared_gtf = self.output_dir / gtf.with_suffix("").name
        if prepared_gtf.exists():
            return prepared_gtf

        with (
            gzip.open(gtf, "rt", encoding="utf-8") as src,
            open(prepared_gtf, "w", encoding="utf-8") as dst,
        ):
            shutil.copyfileobj(src, dst)
        return prepared_gtf

    def prepare_transcriptome_fasta(self, filename: str = "transcripts.fa") -> Path:
        """Build or reuse a transcript FASTA suitable for transcript-level tools."""
        fasta = self.reference.get("fasta")
        gtf = self.reference.get("gtf")
        if not fasta:
            raise RuntimeError(
                f"Reference FASTA is required for quantifier '{self.TOOL_NAME}'."
            )
        fasta_path = Path(fasta)
        if not gtf:
            if self.tool_config.get("fasta_is_transcriptome", False):
                return fasta_path
            raise RuntimeError(
                f"Reference GTF is required for quantifier '{self.TOOL_NAME}'."
            )

        gtf_path = self.prepare_gtf(Path(gtf))
        transcript_fasta = self.output_dir / filename
        if transcript_fasta.exists():
            return transcript_fasta

        if not self._which("gffread"):
            raise RuntimeError("gffread not found. Please install gffread to build transcriptome FASTA.")

        cmd = [
            "gffread",
            "-w",
            str(transcript_fasta),
            "-g",
            str(fasta_path),
            str(gtf_path),
        ]
        run_command(cmd, check=True)
        return transcript_fasta

    def run_per_sample(
        self,
        inputs: dict[str, Any],
        worker: Callable[[str, Any], tuple[str, Any]],
    ) -> dict[str, Any]:
        """Run a worker function for each sample, optionally in parallel."""
        if not inputs:
            return {}

        workers = min(self.get_sample_workers(), len(inputs))
        if workers <= 1:
            return dict(worker(sample, payload) for sample, payload in inputs.items())

        results: dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(worker, sample, payload): sample
                for sample, payload in inputs.items()
            }
            for future in as_completed(future_map):
                sample, value = future.result()
                results[sample] = value
        return results


def register_quantifier(quantifier_cls: type[BaseQuantifier]) -> type[BaseQuantifier]:
    """Register a quantifier implementation in the shared registry."""
    return QuantifierRegistry.register(quantifier_cls)


def discover_alignment_bams(align_dir: Path, samples: list[str]) -> dict[str, Path]:
    """Discover BAM outputs for a set of samples under an alignment directory."""
    discovered: dict[str, Path] = {}
    if not align_dir.exists():
        return discovered

    for sample in samples:
        candidates = [
            align_dir / sample / f"{sample}.bam",
            align_dir / sample / f"{sample}.sorted.bam",
            align_dir / sample / f"{sample}_Aligned.sortedByCoord.out.bam",
            align_dir / f"{sample}.bam",
            align_dir / f"{sample}.sorted.bam",
            align_dir / f"{sample}_Aligned.sortedByCoord.out.bam",
        ]
        for candidate in candidates:
            if candidate.exists():
                discovered[sample] = candidate
                break
    return discovered


def compare_quant_results(results: dict[str, QuantRunResult]) -> pd.DataFrame:
    """Build a pairwise Pearson comparison table across quantification backends."""
    rows: list[dict[str, Any]] = []
    for left_tool, left_result in results.items():
        left_series = left_result.counts_matrix.stack().sort_index()
        for right_tool, right_result in results.items():
            right_series = right_result.counts_matrix.stack().sort_index()
            aligned = pd.concat([left_series, right_series], axis=1, join="inner").fillna(0.0)
            aligned.columns = ["left", "right"]
            pearson = aligned["left"].corr(aligned["right"], method="pearson")
            rows.append(
                {
                    "left_tool": left_tool,
                    "right_tool": right_tool,
                    "pearson": 0.0 if pd.isna(pearson) else float(pearson),
                }
            )
    return pd.DataFrame(rows)


class QuantManager:
    """Extensible quantification analysis manager."""

    def __init__(
        self,
        reads: dict[str, dict],
        reference: dict[str, Path | str | None],
        output_dir: Path,
        threads: int = 4,
        tool: str = DEFAULT_QUANT_TOOL,
        alignments: dict[str, Path] | None = None,
        compare_tools: list[str] | None = None,
        tool_config: dict[str, Any] | None = None,
        compare_tool_configs: dict[str, dict[str, Any]] | None = None,
    ):
        self.reads = reads
        self.reference = reference
        self.output_dir = output_dir
        self.threads = threads
        self.tool = tool
        self.alignments = alignments or {}
        self.compare_tools = compare_tools or []
        self.tool_config = tool_config or {}
        self.compare_tool_configs = compare_tool_configs or {}
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._last_result: QuantRunResult | None = None
        self._comparison_table: pd.DataFrame | None = None
        self._engine_manager = EngineManager(
            domain="quant",
            engine_name=self.tool,
            config=self.tool_config,
        )

    def _resolve_alignments(self, tool_name: str) -> dict[str, Path]:
        """Resolve BAM inputs for alignment-based quantifiers."""
        quantifier_cls = QuantifierRegistry.get(tool_name)
        if not quantifier_cls.REQUIRES_ALIGNMENTS:
            return self.alignments
        if self.alignments:
            return self.alignments

        discovered = discover_alignment_bams(self.output_dir.parent / "align", list(self.reads))
        if discovered:
            logger.info(
                "Recovered alignment BAM files for quantifier '%s' from align directory.",
                tool_name,
            )
        return discovered

    def _create_quantifier(
        self,
        tool_name: str,
        output_dir: Path,
        config: dict[str, Any] | None = None,
    ) -> BaseQuantifier:
        """Instantiate a quantifier through the shared engine manager."""
        manager = self._engine_manager
        if tool_name != manager.engine_name:
            manager.switch_engine(tool_name, config=config or {})
        return cast(
            BaseQuantifier,
            manager.create_engine(
                context=EngineContext(output_dir=output_dir, threads=self.threads, logger=logger),
                config=config or {},
                reads=self.reads,
                reference=self.reference,
                output_dir=output_dir,
                threads=self.threads,
                alignments=self._resolve_alignments(tool_name),
            ),
        )

    def run(self) -> pd.DataFrame:
        """Run the primary quantifier and optional comparison backends."""
        primary_quantifier = self._create_quantifier(self.tool, self.output_dir, self.tool_config)
        primary_result = primary_quantifier.run()
        self._last_result = primary_result

        if self.compare_tools:
            comparison_results = {self.tool: primary_result}
            compare_root = self.output_dir / "comparisons"
            for compare_tool in self.compare_tools:
                compare_dir = compare_root / compare_tool
                compare_quantifier = self._create_quantifier(
                    compare_tool,
                    compare_dir,
                    self.compare_tool_configs.get(compare_tool, {}),
                )
                comparison_results[compare_tool] = compare_quantifier.run()
            self._comparison_table = compare_quant_results(comparison_results)
            self._comparison_table.to_csv(self.output_dir / "tool_comparison.csv", index=False)

        return primary_result.counts_matrix

    def get_stats(self) -> dict[str, Any]:
        """Return sample-level stats from the most recent primary run."""
        if self._last_result is None:
            return {}
        return self._last_result.sample_stats

    def get_comparison_table(self) -> pd.DataFrame | None:
        """Return the cached cross-tool comparison table, if available."""
        return self._comparison_table

    def _build_index(self) -> Any:
        """Compatibility helper that forwards index building to the active quantifier."""
        quantifier = self._create_quantifier(self.tool, self.output_dir, self.tool_config)
        build_index = getattr(quantifier, "build_index", None)
        if build_index is not None:
            return build_index()
        raise AttributeError(f"Quantifier '{self.tool}' does not expose build_index().")

    def _is_salmon_index_complete(self) -> bool:
        """Compatibility helper for checking Salmon index completeness."""
        quantifier = self._create_quantifier(self.tool, self.output_dir, self.tool_config)
        is_index_complete = getattr(quantifier, "is_index_complete", None)
        if is_index_complete is not None:
            return is_index_complete()
        raise AttributeError(f"Quantifier '{self.tool}' does not expose is_index_complete().")

    def _cleanup_incomplete_index(self) -> None:
        """Compatibility helper for removing incomplete Salmon indices."""
        quantifier = self._create_quantifier(self.tool, self.output_dir, self.tool_config)
        cleanup_incomplete_index = getattr(quantifier, "cleanup_incomplete_index", None)
        if cleanup_incomplete_index is not None:
            cleanup_incomplete_index()
            return
        raise AttributeError(f"Quantifier '{self.tool}' does not expose cleanup_incomplete_index().")

    def _prepare_gtf(self, gtf: Path) -> Path:
        """Compatibility helper for preparing compressed GTF files."""
        quantifier = self._create_quantifier(self.tool, self.output_dir, self.tool_config)
        return quantifier.prepare_gtf(gtf)

    def _quantify_sample(self, sample: str, files: dict[str, Any], _out_dir: Path) -> Any:
        """Compatibility helper that proxies per-sample quantification."""
        quantifier = self._create_quantifier(self.tool, self.output_dir, self.tool_config)
        quantify_sample = getattr(quantifier, "quantify_sample", None)
        if quantify_sample is not None:
            return quantify_sample(sample, files)
        raise AttributeError(f"Quantifier '{self.tool}' does not expose quantify_sample().")

    def _merge_counts(self, quant_files: dict[str, Any]) -> pd.DataFrame:
        """Compatibility helper for merging count outputs."""
        quantifier = self._create_quantifier(self.tool, self.output_dir, self.tool_config)
        merge_quantifications = getattr(quantifier, "merge_quantifications", None)
        if merge_quantifications is not None:
            counts, _ = merge_quantifications(quant_files)
            return counts
        raise AttributeError(f"Quantifier '{self.tool}' does not expose merge_quantifications().")


def get_quantifier_required_tools(tool_name: str) -> list[str]:
    """Return external binaries required by a quantifier."""
    quantifier_cls = QuantifierRegistry.get(tool_name)
    return list(quantifier_cls.REQUIRED_BINARIES)


def list_available_quantifiers() -> list[str]:
    """List all registered quantification backends."""
    return QuantifierRegistry.names()


def get_quantifier_specs() -> dict[str, QuantToolSpec]:
    """Return normalized specs for all registered quantifiers."""
    return QuantifierRegistry.specs()
