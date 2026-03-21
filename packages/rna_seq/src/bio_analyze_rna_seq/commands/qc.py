from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_rna_seq.qc import QCManager


def run_qc(
    input_dir: Path = typer.Option(
        ..., "-i", "--input", help="zh: 输入目录 (原始 FastQ)。\nen: Input directory (raw FastQ)."
    ),
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    threads: int = typer.Option(4, "-t", "--threads", help="zh: 线程数。\nen: Number of threads."),
    skip_qc: bool = typer.Option(False, help="zh: 跳过 FastQC/fastp 统计。\nen: Skip FastQC/fastp stats."),
    skip_trim: bool = typer.Option(False, help="zh: 跳过修剪。\nen: Skip trimming."),
    # QC Params
    qualified_quality_phred: int = typer.Option(None, help="zh: 碱基合格的质量值。\nen: Phred quality threshold."),
    unqualified_percent_limit: int = typer.Option(
        None, help="zh: 允许的不合格碱基百分比。\nen: Unqualified percent limit."
    ),
    n_base_limit: int = typer.Option(None, help="zh: 允许的 N 碱基数量。\nen: N base limit."),
    length_required: int = typer.Option(None, help="zh: 所需的最小长度。\nen: Length required."),
    adapter_sequence: str = typer.Option(None, help="zh: read1 的接头序列。\nen: Adapter sequence R1."),
    adapter_sequence_r2: str = typer.Option(None, help="zh: read2 的接头序列。\nen: Adapter sequence R2."),
    dedup: bool = typer.Option(False, help="zh: 启用去重。\nen: Enable deduplication."),
):
    """
    zh: 运行质量控制和修剪。
    en: Run quality control and trimming.
    """
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
