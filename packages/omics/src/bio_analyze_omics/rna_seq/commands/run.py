from __future__ import annotations

import json
from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.commands.utils import load_config, search_and_select_reference
from bio_analyze_omics.rna_seq.pipeline import RNASeqPipeline
from bio_analyze_omics.rna_seq.quant.framework import DEFAULT_QUANT_TOOL


def _load_resume_params(output_dir: Path | None) -> dict:
    """Restore genome-selection-related parameters from an existing pipeline_state.json. """
    if not output_dir:
        return {}

    state_file = output_dir / "pipeline_state.json"
    if not state_file.exists():
        return {}

    try:
        with open(state_file, encoding="utf-8") as handle:
            state = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}

    context = state.get("context", {})
    resume_params = {}
    for key in ("species", "assembly", "provider", "quant_tool"):
        value = context.get(key)
        if value:
            resume_params[key] = value
    compare_tools = context.get("quant_compare_tools")
    if compare_tools:
        resume_params["quant_compare_tools"] = list(compare_tools)
    quant_config = context.get("quant_config")
    if quant_config:
        resume_params["quant_config"] = quant_config

    for key in ("genome_fasta", "genome_gtf"):
        value = context.get(key)
        if value:
            path = Path(value)
            if path.exists():
                resume_params[key] = path

    ref_info = context.get("ref_info") or {}
    for source_key, target_key in (("fasta", "genome_fasta"), ("gtf", "genome_gtf")):
        if target_key in resume_params:
            continue
        value = ref_info.get(source_key)
        if value:
            path = Path(value)
            if path.exists():
                resume_params[target_key] = path

    return resume_params


def run_analysis(
    config_file: Path = Option(
        None,
        "--config",
        "-c",
        help=_("Path to JSON/YAML config file. Overrides other options if provided."),
    ),
    input_dir: Path = Option(
        None,
        "--input",
        "-i",
        help=_("Directory containing raw FastQ files. Required if --sra-ids is not provided."),
    ),
    sra_ids: list[str] = Option(
        None,
        "--sra-id",
        help=_("SRA Accession IDs to download and process (e.g. SRR123456)."),
    ),
    output_dir: Path = Option(
        None, "--output", "-o", help=_("Directory for analysis results.")
    ),
    design_file: Path = Option(
        None,
        "--design",
        "-d",
        help=_("CSV file describing experimental design (columns: sample, condition, ...)."),
    ),
    species: str = Option(
        None,
        "--species",
        "-s",
        help=_("Species name for auto-downloading reference genome (e.g. 'Homo sapiens')."),
    ),
    assembly: str = Option(
        None,
        "--assembly",
        help=_(
            "Reference assembly accession, e.g. GCA_013347765.1. "
            "Takes precedence over --species for auto-download."
        ),
    ),
    genome_fasta: Path = Option(
        None,
        "--genome-fasta",
        help=_("Path to reference genome FASTA file (overrides --species/--assembly auto-download)."),
    ),
    genome_gtf: Path = Option(
        None,
        "--genome-gtf",
        help=_("Path to reference genome GTF annotation file (overrides --species/--assembly auto-download)."),
    ),
    threads: int = Option(4, "--threads", "-t", help=_("Number of threads to use.")),
    skip_qc: bool = Option(False, "--skip-qc", help=_("Skip Quality Control step.")),
    skip_trim: bool = Option(False, "--skip-trim", help=_("Skip Trimming step.")),
    # Align Options
    star_align: bool = Option(
        False,
        "--star-align",
        help=_("Enable STAR alignment and chromosome distribution analysis."),
    ),
    theme: str = Option(
        "default",
        "--theme",
        help=_("Plotting theme (default, nature, science, or custom package name)."),
    ),
    quant_tool: str = Option(
        DEFAULT_QUANT_TOOL,
        "--quant-tool",
        help=(
            """Quantification backend."""
        ),
    ),
    quant_compare_tools: list[str] = Option(
        None,
        "--quant-compare-tool",
        help=_("Comparison quantifiers, repeatable."),
    ),
    step: str = Option(
        None,
        "--step",
        help=_("Run only a specific step (qc, quant, de, enrichment, report). If None, run all."),
    ),
    # QC Options
    qualified_quality_phred: int = Option(
        None,
        help=_("The quality value that a base is qualified. Default 15 means Phred quality >= Q15."),
    ),
    unqualified_percent_limit: int = Option(
        None,
        help=_("How many percents of bases are allowed to be unqualified (0~100). Default 40 means 40%."),
    ),
    n_base_limit: int = Option(
        None, help=_("How many N bases are allowed. Default 5.")
    ),
    length_required: int = Option(
        None,
        help=_("Reads shorter than length_required will be discarded. Default 15."),
    ),
    max_len1: int = Option(
        None,
        help=_("If read1 is longer than max_len1, trim it at tail. Default 0 (no trim)."),
    ),
    max_len2: int = Option(
        None,
        help=_("If read2 is longer than max_len2, trim it at tail. Default 0 (no trim)."),
    ),
    adapter_sequence: str = Option(
        None,
        help=_("Adapter sequence for read1. Auto-detected if not provided."),
    ),
    adapter_sequence_r2: str = Option(
        None,
        help=_("Adapter sequence for read2. Auto-detected if not provided."),
    ),
    trim_front1: int = Option(
        None, help=_("Trimming how many bases in front for read1.")
    ),
    trim_tail1: int = Option(
        None, help=_("Trimming how many bases in tail for read1.")
    ),
    cut_right: bool = Option(
        False, help=_("Enable cut_right (sliding window trimming).")
    ),
    cut_window_size: int = Option(
        None, help=_("Window size for cut_right. Default 4.")
    ),
    cut_mean_quality: int = Option(
        None,
        help=_("Mean quality requirement for cut_right. Default 20."),
    ),
    dedup: bool = Option(False, help=_("Enable deduplication.")),
    poly_g_min_len: int = Option(
        None,
        help=_("Minimum length for polyG tail trimming. Default 10."),
    ),
) -> None:
    """
    Run the complete RNA-Seq analysis pipeline.

    Parameters can be specified via command line arguments or a configuration file.
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
        "assembly": assembly,
        "provider": None,
        "genome_fasta": genome_fasta,
        "genome_gtf": genome_gtf,
        "threads": threads,
        "skip_qc": skip_qc,
        "skip_trim": skip_trim,
        "star_align": star_align,
        "sra_ids": sra_ids,
        "step": step,
        "quant_tool": quant_tool,
        "quant_compare_tools": quant_compare_tools or [],
        "quant_config": {},
        "theme": theme,
    }

    if config:
        for key, value in config.items():
            if key in ["input_dir", "output_dir", "design_file", "genome_fasta", "genome_gtf"]:
                if value:
                    params[key] = Path(value)
            elif key in params:
                params[key] = value

        config_quant = config.get("quant", {})
        if isinstance(config_quant, dict):
            if config_quant.get("tool"):
                params["quant_tool"] = config_quant["tool"]
            if config_quant.get("compare_tools"):
                params["quant_compare_tools"] = list(config_quant["compare_tools"])
            params["quant_config"] = {
                "primary": config_quant.get("primary", {}),
                "compare": config_quant.get("compare", {}),
            }

    resume_params = _load_resume_params(params.get("output_dir"))
    for key, value in resume_params.items():
        if not params.get(key):
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
        echo("Error: --output / output_dir is required (either in CLI or config).", err=True)
        raise Exit(code=1)

    if not params.get("design_file"):
        echo("Error: --design / design_file is required (either in CLI or config).", err=True)
        raise Exit(code=1)

    if not params.get("input_dir") and not params.get("sra_ids") and not params.get("step"):
        echo(
            "Error: Either --input / input_dir or --sra-id / sra_ids must be provided.",
            err=True,
        )
        raise Exit(code=1)

    if params.get("species") and not params.get("assembly") and not params.get("genome_fasta"):
        selected_query, selected_provider = search_and_select_reference(params["species"])
        params["assembly"] = selected_query
        params["provider"] = selected_provider

    pipeline = RNASeqPipeline(
        input_dir=params.get("input_dir"),
        output_dir=params["output_dir"],
        design_file=params["design_file"],
        species=params.get("species"),
        assembly=params.get("assembly"),
        provider=params.get("provider"),
        genome_fasta=params.get("genome_fasta"),
        genome_gtf=params.get("genome_gtf"),
        threads=params.get("threads", 4),
        skip_qc=params.get("skip_qc", False),
        skip_trim=params.get("skip_trim", False),
        sra_ids=params.get("sra_ids"),
        step=params.get("step"),
        qc_params=final_qc_params,
        star_align=params.get("star_align", False),
        quant_tool=params.get("quant_tool", DEFAULT_QUANT_TOOL),
        quant_compare_tools=params.get("quant_compare_tools", []),
        quant_config=params.get("quant_config", {}),
        theme=params.get("theme", "default"),
    )
    pipeline.run()
