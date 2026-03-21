from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_rna_seq.genome import GenomeManager


def prepare_genome(
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    species: str = typer.Option(None, "-s", "--species", help="zh: 物种名称。\nen: Species name."),
    fasta: Path = typer.Option(None, "--fasta", help="zh: 基因组 FASTA 文件。\nen: Genome FASTA file."),
    gtf: Path = typer.Option(None, "--gtf", help="zh: 基因组 GTF 文件。\nen: Genome GTF file."),
):
    """
    zh: 准备参考基因组（下载或索引）。
    en: Prepare reference genome (download or index).
    """
    if not species and not fasta:
        typer.echo("Error: Either --species or --fasta must be provided.", err=True)
        raise typer.Exit(code=1)

    mgr = GenomeManager(species=species, fasta=fasta, gtf=gtf, output_dir=output_dir)
    mgr.prepare()
    typer.echo(f"Genome prepared in {output_dir}")
