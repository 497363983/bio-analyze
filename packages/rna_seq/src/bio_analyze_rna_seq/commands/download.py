from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_rna_seq.sra import SRAManager


def download_sra(
    sra_ids: list[str] = typer.Argument(..., help="zh: SRA Accession ID 列表。\nen: List of SRA Accession IDs."),
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    threads: int = typer.Option(4, "-t", "--threads", help="zh: 线程数。\nen: Number of threads."),
):
    """
    zh: 从 SRA 下载 FastQ 文件。
    en: Download FastQ files from SRA.
    """
    mgr = SRAManager(output_dir=output_dir, threads=threads)
    mgr.download(sra_ids)
    typer.echo(f"Downloaded {len(sra_ids)} samples to {output_dir}")
