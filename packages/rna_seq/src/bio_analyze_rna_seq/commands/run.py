from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_rna_seq.commands.utils import load_config
from bio_analyze_rna_seq.pipeline import RNASeqPipeline


def run_analysis(
    config_file: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="zh: JSON/YAML 配置文件路径。如果提供，将覆盖其他选项。\nen: Path to JSON/YAML config file. Overrides other options if provided.",
    ),
    input_dir: Path = typer.Option(
        None,
        "--input",
        "-i",
        help="zh: 包含原始 FastQ 文件的目录。如果未提供 --sra-ids，则是必需的。\nen: Directory containing raw FastQ files. Required if --sra-ids is not provided.",
    ),
    sra_ids: list[str] = typer.Option(
        None,
        "--sra-id",
        help="zh: 要下载和处理的 SRA Accession ID 列表 (例如 SRR123456)。\nen: SRA Accession IDs to download and process (e.g. SRR123456).",
    ),
    output_dir: Path = typer.Option(
        None, "--output", "-o", help="zh: 分析结果输出目录。\nen: Directory for analysis results."
    ),
    design_file: Path = typer.Option(
        None,
        "--design",
        "-d",
        help="zh: 描述实验设计的 CSV 文件 (包含 sample, condition 等列)。\nen: CSV file describing experimental design (columns: sample, condition, ...).",
    ),
    species: str = typer.Option(
        None,
        "--species",
        "-s",
        help="zh: 用于自动下载参考基因组的物种名称 (例如 'Homo sapiens')。\nen: Species name for auto-downloading reference genome (e.g. 'Homo sapiens').",
    ),
    genome_fasta: Path = typer.Option(
        None,
        "--genome-fasta",
        help="zh: 参考基因组 FASTA 文件路径 (覆盖 --species)。\nen: Path to reference genome FASTA file (overrides --species).",
    ),
    genome_gtf: Path = typer.Option(
        None,
        "--genome-gtf",
        help="zh: 参考基因组 GTF 注释文件路径 (覆盖 --species)。\nen: Path to reference genome GTF annotation file (overrides --species).",
    ),
    threads: int = typer.Option(4, "--threads", "-t", help="zh: 使用的线程数。\nen: Number of threads to use."),
    skip_qc: bool = typer.Option(False, "--skip-qc", help="zh: 跳过质量控制步骤。\nen: Skip Quality Control step."),
    skip_trim: bool = typer.Option(False, "--skip-trim", help="zh: 跳过修剪步骤。\nen: Skip Trimming step."),
    # Align Options
    star_align: bool = typer.Option(
        False,
        "--star-align",
        help="zh: 启用 STAR 比对和染色体分布分析。\nen: Enable STAR alignment and chromosome distribution analysis.",
    ),
    theme: str = typer.Option(
        "default",
        "--theme",
        help="zh: 绘图主题 (default, nature, science 或自定义包名)。\nen: Plotting theme (default, nature, science, or custom package name).",
    ),
    step: str = typer.Option(
        None,
        "--step",
        help="zh: 仅运行特定步骤 (qc, quant, de, enrichment, report)。如果为 None，则运行所有步骤。\nen: Run only a specific step (qc, quant, de, enrichment, report). If None, run all.",
    ),
    # QC Options
    qualified_quality_phred: int = typer.Option(
        None,
        help="zh: 碱基合格的质量值。默认 15 表示 Phred 质量 >= Q15。\nen: The quality value that a base is qualified. Default 15 means Phred quality >= Q15.",
    ),
    unqualified_percent_limit: int = typer.Option(
        None,
        help="zh: 允许的不合格碱基百分比 (0~100)。默认 40 表示 40%。\nen: How many percents of bases are allowed to be unqualified (0~100). Default 40 means 40%.",
    ),
    n_base_limit: int = typer.Option(
        None, help="zh: 允许的 N 碱基数量。默认为 5。\nen: How many N bases are allowed. Default 5."
    ),
    length_required: int = typer.Option(
        None,
        help="zh: 短于 length_required 的 Reads 将被丢弃。默认为 15。\nen: Reads shorter than length_required will be discarded. Default 15.",
    ),
    max_len1: int = typer.Option(
        None,
        help="zh: 如果 read1 长于 max_len1，则在尾部修剪。默认 0 (不修剪)。\nen: If read1 is longer than max_len1, trim it at tail. Default 0 (no trim).",
    ),
    max_len2: int = typer.Option(
        None,
        help="zh: 如果 read2 长于 max_len2，则在尾部修剪。默认 0 (不修剪)。\nen: If read2 is longer than max_len2, trim it at tail. Default 0 (no trim).",
    ),
    adapter_sequence: str = typer.Option(
        None,
        help="zh: read1 的接头序列。如果未提供，则自动检测。\nen: Adapter sequence for read1. Auto-detected if not provided.",
    ),
    adapter_sequence_r2: str = typer.Option(
        None,
        help="zh: read2 的接头序列。如果未提供，则自动检测。\nen: Adapter sequence for read2. Auto-detected if not provided.",
    ),
    trim_front1: int = typer.Option(
        None, help="zh: read1 头部修剪的碱基数。\nen: Trimming how many bases in front for read1."
    ),
    trim_tail1: int = typer.Option(
        None, help="zh: read1 尾部修剪的碱基数。\nen: Trimming how many bases in tail for read1."
    ),
    cut_right: bool = typer.Option(
        False, help="zh: 启用 cut_right (滑动窗口修剪)。\nen: Enable cut_right (sliding window trimming)."
    ),
    cut_window_size: int = typer.Option(
        None, help="zh: cut_right 的窗口大小。默认为 4。\nen: Window size for cut_right. Default 4."
    ),
    cut_mean_quality: int = typer.Option(
        None,
        help="zh: cut_right 的平均质量要求。默认为 20。\nen: Mean quality requirement for cut_right. Default 20.",
    ),
    dedup: bool = typer.Option(False, help="zh: 启用去重。\nen: Enable deduplication."),
    poly_g_min_len: int = typer.Option(
        None,
        help="zh: polyG 尾部修剪的最小长度。默认为 10。\nen: Minimum length for polyG tail trimming. Default 10.",
    ),
) -> None:
    """
    zh: 运行完整的 RNA-Seq 分析流程。
    en: Run the complete RNA-Seq analysis pipeline.

    zh: 可以通过命令行参数或配置文件指定参数。
    en: Parameters can be specified via command line arguments or a configuration file.
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
