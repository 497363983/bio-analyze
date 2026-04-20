from __future__ import annotations

from pathlib import Path

import pandas as pd

from bio_analyze_core.cli.app import Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.enrichment import EnrichmentManager


def run_gsea(
    de_results: Path = Option(
        ..., "--de-results", help=_("DESeq2 results CSV file.")
    ),
    species: str = Option(
        ..., "-s", "--species", help=_("Species name (e.g. 'Homo sapiens').")
    ),
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    gene_sets: str = Option(
        "KEGG_2021_Human",
        help=_("Gene sets library (e.g. KEGG_2021_Human, GO_Biological_Process_2021)."),
    ),
    ranking_metric: str = Option(
        "auto",
        help=_("Column for ranking (auto, stat, log2FoldChange)."),
    ),
    top_n: int = Option(5, help=_("Number of top pathways to plot.")),
    theme: str = Option("default", help=_("Plot theme.")),
):
    """Run GSEA analysis. """
    de_df = pd.read_csv(de_results, index_col=0)
    mgr = EnrichmentManager(de_results=de_df, species=species, output_dir=output_dir, theme=theme)
    mgr.run_gsea(gene_sets=gene_sets, ranking_metric=ranking_metric, top_n_plot=top_n)
    echo(f"GSEA analysis completed. Results in {output_dir}/GSEA")
