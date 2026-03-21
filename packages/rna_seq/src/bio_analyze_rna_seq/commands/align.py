from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_rna_seq.align import StarAlignmentManager
from bio_analyze_rna_seq.commands.utils import detect_clean_reads


def run_align(
    input_dir: Path = typer.Option(
        ..., "-i", "--input", help="zh: 包含 clean FastQ 文件的目录。\nen: Directory with clean FastQ files."
    ),
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    fasta: Path = typer.Option(..., "--fasta", help="zh: 基因组 FASTA 文件。\nen: Genome FASTA file."),
    gtf: Path = typer.Option(None, "--gtf", help="zh: 基因组 GTF 文件。\nen: Genome GTF file."),
    threads: int = typer.Option(4, "-t", "--threads", help="zh: 线程数。\nen: Number of threads."),
    theme: str = typer.Option("default", help="zh: 绘图主题。\nen: Plot theme."),
):
    """
    zh: 运行 STAR 比对。
    en: Run STAR alignment.
    """
    reads = detect_clean_reads(input_dir)
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
