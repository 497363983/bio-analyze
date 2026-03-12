from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import typer
import yaml

from .align import StarAlignmentManager
from .de import DEManager
from .enrichment import EnrichmentManager
from .genome import GenomeManager
from .pipeline import RNASeqPipeline
from .qc import QCManager
from .quant import QuantManager
from .sra import SRAManager


def load_config(config_file: Path) -> dict[str, Any]:
    """从 JSON 或 YAML 文件加载配置。"""
    if config_file.suffix in (".json",):
        with open(config_file, encoding="utf-8") as f:
            return json.load(f)
    elif config_file.suffix in (".yaml", ".yml"):
        with open(config_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Config file must be .json or .yaml/.yml")


def _detect_clean_reads(input_dir: Path) -> dict[str, dict]:
    """
    从 QC 输出目录检测 clean reads。
    假设文件命名为 {sample}_clean_R1.fastq.gz
    """
    # 使用 QCManager 的检测逻辑查找文件
    temp_mgr = QCManager(input_dir, input_dir)
    raw_samples = temp_mgr._detect_files(input_dir)

    clean_samples = {}
    for sample, files in raw_samples.items():
        # QCManager 可能会将 "sample_clean" 检测为样本名，如果后缀是 _clean_R1
        # 所以我们从样本名中去除 "_clean"
        real_name = sample.replace("_clean", "")
        clean_samples[real_name] = files

    return clean_samples


def get_app() -> typer.Typer:
    app = typer.Typer(help="Transcriptomics analysis workflow.")

    @app.command("run")
    def run_analysis(
        config_file: Path = typer.Option(
            None,
            "--config",
            "-c",
            help="Path to JSON/YAML config file. Overrides other options if provided.",
        ),
        input_dir: Path = typer.Option(
            None,
            "--input",
            "-i",
            help="Directory containing raw FastQ files. Required if --sra-ids is not provided.",
        ),
        sra_ids: list[str] = typer.Option(
            None, "--sra-id", help="SRA Accession IDs to download and process (e.g. SRR123456)."
        ),
        output_dir: Path = typer.Option(None, "--output", "-o", help="Directory for analysis results."),
        design_file: Path = typer.Option(
            None,
            "--design",
            "-d",
            help="CSV file describing experimental design (columns: sample, condition, ...).",
        ),
        species: str = typer.Option(
            None,
            "--species",
            "-s",
            help="Species name for auto-downloading reference genome (e.g. 'Homo sapiens').",
        ),
        genome_fasta: Path = typer.Option(
            None,
            "--genome-fasta",
            help="Path to reference genome FASTA file (overrides --species).",
        ),
        genome_gtf: Path = typer.Option(
            None,
            "--genome-gtf",
            help="Path to reference genome GTF annotation file (overrides --species).",
        ),
        threads: int = typer.Option(4, "--threads", "-t", help="Number of threads to use."),
        skip_qc: bool = typer.Option(False, "--skip-qc", help="Skip Quality Control step."),
        skip_trim: bool = typer.Option(False, "--skip-trim", help="Skip Trimming step."),
        # Align Options
        star_align: bool = typer.Option(
            False, "--star-align", help="Enable STAR alignment and chromosome distribution analysis."
        ),
        theme: str = typer.Option(
            "default", "--theme", help="Plotting theme (default, nature, science, or custom package name)."
        ),
        step: str = typer.Option(
            None,
            "--step",
            help="Run only a specific step (qc, quant, de, enrichment, report). If None, run all.",
        ),
        # QC Options
        qualified_quality_phred: int = typer.Option(
            None, help="The quality value that a base is qualified. Default 15 means Phred quality >= Q15."
        ),
        unqualified_percent_limit: int = typer.Option(
            None, help="How many percents of bases are allowed to be unqualified (0~100). Default 40 means 40%."
        ),
        n_base_limit: int = typer.Option(None, help="How many N bases are allowed. Default 5."),
        length_required: int = typer.Option(
            None, help="Reads shorter than length_required will be discarded. Default 15."
        ),
        max_len1: int = typer.Option(
            None, help="If read1 is longer than max_len1, trim it at tail. Default 0 (no trim)."
        ),
        max_len2: int = typer.Option(
            None, help="If read2 is longer than max_len2, trim it at tail. Default 0 (no trim)."
        ),
        adapter_sequence: str = typer.Option(None, help="Adapter sequence for read1. Auto-detected if not provided."),
        adapter_sequence_r2: str = typer.Option(
            None, help="Adapter sequence for read2. Auto-detected if not provided."
        ),
        trim_front1: int = typer.Option(None, help="Trimming how many bases in front for read1."),
        trim_tail1: int = typer.Option(None, help="Trimming how many bases in tail for read1."),
        cut_right: bool = typer.Option(False, help="Enable cut_right (sliding window trimming)."),
        cut_window_size: int = typer.Option(None, help="Window size for cut_right. Default 4."),
        cut_mean_quality: int = typer.Option(None, help="Mean quality requirement for cut_right. Default 20."),
        dedup: bool = typer.Option(False, help="Enable deduplication."),
        poly_g_min_len: int = typer.Option(None, help="Minimum length for polyG tail trimming. Default 10."),
    ) -> None:
        """
        运行完整的 RNA-Seq 分析流程。
        可以通过命令行参数或配置文件指定参数。
        """
        # 如果提供了配置文件，加载并覆盖默认值
        config = {}
        if config_file:
            config = load_config(config_file)

        params = {
            "input_dir": input_dir,
            "output_dir": output_dir,
            "design_file": design_file,
            "species": species,
            "genome_fasta": genome_fasta,
            "genome_gtf": genome_gtf,
            "threads": threads,
            "skip_qc": skip_qc,
            "skip_trim": skip_trim,
            "star_align": star_align,
            "sra_ids": sra_ids,
            "step": step,
            "theme": theme,
        }

        if config:
            for key, value in config.items():
                if key in ["input_dir", "output_dir", "design_file", "genome_fasta", "genome_gtf"]:
                    if value:
                        params[key] = Path(value)
                elif key in params:
                    params[key] = value

        qc_params_dict = {
            "qualified_quality_phred": qualified_quality_phred,
            "unqualified_percent_limit": unqualified_percent_limit,
            "n_base_limit": n_base_limit,
            "length_required": length_required,
            "max_len1": max_len1,
            "max_len2": max_len2,
            "adapter_sequence": adapter_sequence,
            "adapter_sequence_r2": adapter_sequence_r2,
            "trim_front1": trim_front1,
            "trim_tail1": trim_tail1,
            "cut_right": cut_right,
            "cut_window_size": cut_window_size,
            "cut_mean_quality": cut_mean_quality,
            "dedup": dedup,
            "poly_g_min_len": poly_g_min_len,
        }

        config_qc = config.get("qc", {})

        final_qc_params = {}
        for k, v in qc_params_dict.items():
            if v is not None and v is not False:
                final_qc_params[k] = v
            elif k in config_qc:
                final_qc_params[k] = config_qc[k]

        if not params.get("output_dir"):
            typer.echo("Error: --output / output_dir is required (either in CLI or config).", err=True)
            raise typer.Exit(code=1)

        if not params.get("design_file"):
            typer.echo("Error: --design / design_file is required (either in CLI or config).", err=True)
            raise typer.Exit(code=1)

        if not params.get("input_dir") and not params.get("sra_ids") and not params.get("step"):
            typer.echo(
                "Error: Either --input / input_dir or --sra-id / sra_ids must be provided.",
                err=True,
            )
            raise typer.Exit(code=1)

        pipeline = RNASeqPipeline(
            input_dir=params.get("input_dir"),
            output_dir=params["output_dir"],
            design_file=params["design_file"],
            species=params.get("species"),
            genome_fasta=params.get("genome_fasta"),
            genome_gtf=params.get("genome_gtf"),
            threads=params.get("threads", 4),
            skip_qc=params.get("skip_qc", False),
            skip_trim=params.get("skip_trim", False),
            sra_ids=params.get("sra_ids"),
            step=params.get("step"),
            qc_params=final_qc_params,
            star_align=params.get("star_align", False),
            theme=params.get("theme", "default"),
        )
        pipeline.run()

    @app.command("download")
    def download_sra(
        sra_ids: list[str] = typer.Argument(..., help="List of SRA Accession IDs."),
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        threads: int = typer.Option(4, "-t", "--threads", help="Number of threads."),
    ):
        """从 SRA 下载 FastQ 文件。"""
        mgr = SRAManager(output_dir=output_dir, threads=threads)
        mgr.download(sra_ids)
        typer.echo(f"Downloaded {len(sra_ids)} samples to {output_dir}")

    @app.command("genome")
    def prepare_genome(
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        species: str = typer.Option(None, "-s", "--species", help="Species name."),
        fasta: Path = typer.Option(None, "--fasta", help="Genome FASTA file."),
        gtf: Path = typer.Option(None, "--gtf", help="Genome GTF file."),
    ):
        """准备参考基因组（下载或索引）。"""
        if not species and not fasta:
            typer.echo("Error: Either --species or --fasta must be provided.", err=True)
            raise typer.Exit(code=1)

        mgr = GenomeManager(species=species, fasta=fasta, gtf=gtf, output_dir=output_dir)
        mgr.prepare()
        typer.echo(f"Genome prepared in {output_dir}")

    @app.command("qc")
    def run_qc(
        input_dir: Path = typer.Option(..., "-i", "--input", help="Input directory (raw FastQ)."),
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        threads: int = typer.Option(4, "-t", "--threads", help="Number of threads."),
        skip_qc: bool = typer.Option(False, help="Skip FastQC/fastp stats."),
        skip_trim: bool = typer.Option(False, help="Skip trimming."),
        # QC Params
        qualified_quality_phred: int = typer.Option(None, help="Phred quality threshold."),
        unqualified_percent_limit: int = typer.Option(None, help="Unqualified percent limit."),
        n_base_limit: int = typer.Option(None, help="N base limit."),
        length_required: int = typer.Option(None, help="Length required."),
        adapter_sequence: str = typer.Option(None, help="Adapter sequence R1."),
        adapter_sequence_r2: str = typer.Option(None, help="Adapter sequence R2."),
        dedup: bool = typer.Option(False, help="Enable deduplication."),
    ):
        """运行质量控制和修剪。"""
        mgr = QCManager(
            input_dir=input_dir,
            output_dir=output_dir,
            threads=threads,
            skip_qc=skip_qc,
            skip_trim=skip_trim,
            qualified_quality_phred=qualified_quality_phred,
            unqualified_percent_limit=unqualified_percent_limit,
            n_base_limit=n_base_limit,
            length_required=length_required,
            adapter_sequence=adapter_sequence,
            adapter_sequence_r2=adapter_sequence_r2,
            dedup=dedup,
        )
        mgr.run()
        typer.echo(f"QC completed. Results in {output_dir}")

    @app.command("align")
    def run_align(
        input_dir: Path = typer.Option(..., "-i", "--input", help="Directory with clean FastQ files."),
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        fasta: Path = typer.Option(..., "--fasta", help="Genome FASTA file."),
        gtf: Path = typer.Option(None, "--gtf", help="Genome GTF file."),
        threads: int = typer.Option(4, "-t", "--threads", help="Number of threads."),
        theme: str = typer.Option("default", help="Plot theme."),
    ):
        """运行 STAR 比对。"""
        reads = _detect_clean_reads(input_dir)
        if not reads:
            typer.echo(f"No clean reads found in {input_dir}", err=True)
            raise typer.Exit(code=1)

        reference = {"fasta": fasta}
        if gtf:
            reference["gtf"] = gtf

        mgr = StarAlignmentManager(
            reads=reads, reference=reference, output_dir=output_dir, threads=threads, theme=theme
        )
        mgr.run()
        typer.echo(f"Alignment completed. Results in {output_dir}")

    @app.command("quant")
    def run_quant(
        input_dir: Path = typer.Option(..., "-i", "--input", help="Directory with clean FastQ files."),
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        fasta: Path = typer.Option(..., "--fasta", help="Genome/Transcriptome FASTA file."),
        gtf: Path = typer.Option(None, "--gtf", help="Genome GTF file (optional if FASTA is transcriptome)."),
        threads: int = typer.Option(4, "-t", "--threads", help="Number of threads."),
    ):
        """运行 Salmon 定量。"""
        reads = _detect_clean_reads(input_dir)
        if not reads:
            typer.echo(f"No clean reads found in {input_dir}", err=True)
            raise typer.Exit(code=1)

        reference = {"fasta": fasta}
        if gtf:
            reference["gtf"] = gtf

        mgr = QuantManager(reads=reads, reference=reference, output_dir=output_dir, threads=threads)
        mgr.run()
        typer.echo(f"Quantification completed. Results in {output_dir}")

    @app.command("de")
    def run_de(
        counts: Path = typer.Option(..., "--counts", help="Counts matrix CSV file."),
        design: Path = typer.Option(..., "--design", help="Design matrix CSV file."),
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        theme: str = typer.Option("default", help="Plot theme."),
    ):
        """运行差异表达分析 (DESeq2)。"""
        counts_df = pd.read_csv(counts, index_col=0)
        mgr = DEManager(counts=counts_df, design_file=design, output_dir=output_dir, theme=theme)
        mgr.run()
        typer.echo(f"DE analysis completed. Results in {output_dir}")

    @app.command("enrich")
    def run_enrich(
        de_results: Path = typer.Option(..., "--de-results", help="DESeq2 results CSV file."),
        species: str = typer.Option(..., "-s", "--species", help="Species name (e.g. 'Homo sapiens')."),
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        theme: str = typer.Option("default", help="Plot theme."),
    ):
        """运行富集分析 (GO/KEGG)。"""
        de_df = pd.read_csv(de_results, index_col=0)
        mgr = EnrichmentManager(de_results=de_df, species=species, output_dir=output_dir, theme=theme)
        mgr.run()
        typer.echo(f"Enrichment analysis completed. Results in {output_dir}")

    @app.command("gsea")
    def run_gsea(
        de_results: Path = typer.Option(..., "--de-results", help="DESeq2 results CSV file."),
        species: str = typer.Option(..., "-s", "--species", help="Species name (e.g. 'Homo sapiens')."),
        output_dir: Path = typer.Option(..., "-o", "--output", help="Output directory."),
        gene_sets: str = typer.Option(
            "KEGG_2021_Human", help="Gene sets library (e.g. KEGG_2021_Human, GO_Biological_Process_2021)."
        ),
        ranking_metric: str = typer.Option("auto", help="Column for ranking (auto, stat, log2FoldChange)."),
        top_n: int = typer.Option(5, help="Number of top pathways to plot."),
        theme: str = typer.Option("default", help="Plot theme."),
    ):
        """运行 GSEA 分析。"""
        de_df = pd.read_csv(de_results, index_col=0)
        mgr = EnrichmentManager(de_results=de_df, species=species, output_dir=output_dir, theme=theme)
        mgr.run_gsea(gene_sets=gene_sets, ranking_metric=ranking_metric, top_n_plot=top_n)
        typer.echo(f"GSEA analysis completed. Results in {output_dir}/GSEA")

    return app
