from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from bio_analyze_rna_seq.enrichment import EnrichmentManager


def run_gsea(
    de_results: Path = typer.Option(
        ..., "--de-results", help="zh: DESeq2 结果 CSV 文件。\nen: DESeq2 results CSV file."
    ),
    species: str = typer.Option(
        ..., "-s", "--species", help="zh: 物种名称 (例如 'Homo sapiens')。\nen: Species name (e.g. 'Homo sapiens')."
    ),
    output_dir: Path = typer.Option(..., "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
    gene_sets: str = typer.Option(
        "KEGG_2021_Human",
        help="zh: 基因集库 (例如 KEGG_2021_Human, GO_Biological_Process_2021)。\nen: Gene sets library (e.g. KEGG_2021_Human, GO_Biological_Process_2021).",
    ),
    ranking_metric: str = typer.Option(
        "auto",
        help="zh: 排名列 (auto, stat, log2FoldChange)。\nen: Column for ranking (auto, stat, log2FoldChange).",
    ),
    top_n: int = typer.Option(5, help="zh: 绘制的顶部通路数量。\nen: Number of top pathways to plot."),
    theme: str = typer.Option("default", help="zh: 绘图主题。\nen: Plot theme."),
):
    """
    zh: 运行 GSEA 分析。
    en: Run GSEA analysis.
    """
    de_df = pd.read_csv(de_results, index_col=0)
    mgr = EnrichmentManager(de_results=de_df, species=species, output_dir=output_dir, theme=theme)
    mgr.run_gsea(gene_sets=gene_sets, ranking_metric=ranking_metric, top_n_plot=top_n)
    typer.echo(f"GSEA analysis completed. Results in {output_dir}/GSEA")
