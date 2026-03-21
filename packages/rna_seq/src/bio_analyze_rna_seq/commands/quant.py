from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_rna_seq.commands.utils import detect_clean_reads
from bio_analyze_rna_seq.quant import QuantManager


def run_quant(
    input_dir: Path = typer.Option(
        ..., "-i", "--input", help="zh: 包含 clean FastQ 文件的目录。\nen: Directory with clean FastQ files."
    ),
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    fasta: Path = typer.Option(
        ..., "--fasta", help="zh: 基因组/转录组 FASTA 文件。\nen: Genome/Transcriptome FASTA file."
    ),
    gtf: Path = typer.Option(
        None,
        "--gtf",
        help="zh: 基因组 GTF 文件 (如果 FASTA 是转录组则可选)。\nen: Genome GTF file (optional if FASTA is transcriptome).",
    ),
    threads: int = typer.Option(4, "-t", "--threads", help="zh: 线程数。\nen: Number of threads."),
):
    """
    zh: 运行 Salmon 定量。
    en: Run Salmon quantification.
    """
    reads = detect_clean_reads(input_dir)
    if not reads:
        typer.echo(f"No clean reads found in {input_dir}", err=True)
        raise typer.Exit(code=1)

    reference = {"fasta": fasta}
    if gtf:
        reference["gtf"] = gtf

    mgr = QuantManager(reads=reads, reference=reference, output_dir=output_dir, threads=threads)
    mgr.run()
    typer.echo(f"Quantification completed. Results in {output_dir}")
