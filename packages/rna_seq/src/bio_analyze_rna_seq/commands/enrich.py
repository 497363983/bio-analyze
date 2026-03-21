from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from bio_analyze_rna_seq.enrichment import EnrichmentManager


def run_enrich(
    de_results: Path = typer.Option(
        ..., "--de-results", help="zh: DESeq2 结果 CSV 文件。\nen: DESeq2 results CSV file."
    ),
    species: str = typer.Option(
        ..., "-s", "--species", help="zh: 物种名称 (例如 'Homo sapiens')。\nen: Species name (e.g. 'Homo sapiens')."
    ),
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    theme: str = typer.Option("default", help="zh: 绘图主题。\nen: Plot theme."),
):
    """
    zh: 运行富集分析 (GO/KEGG)。
    en: Run enrichment analysis (GO/KEGG).
    """
    de_df = pd.read_csv(de_results, index_col=0)
    mgr = EnrichmentManager(de_results=de_df, species=species, output_dir=output_dir, theme=theme)
    mgr.run()
    typer.echo(f"Enrichment analysis completed. Results in {output_dir}")
