from __future__ import annotations

from pathlib import Path

import pandas as pd

from bio_analyze_core.cli.app import Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.enrichment import EnrichmentManager


def run_enrich(
    de_results: Path = Option(
        ..., "--de-results", help=_("DESeq2 results CSV file.")
    ),
    species: str = Option(
        ..., "-s", "--species", help=_("Species name (e.g. 'Homo sapiens').")
    ),
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    theme: str = Option("default", help=_("Plot theme.")),
):
    """Run enrichment analysis (GO/KEGG). """
    de_df = pd.read_csv(de_results, index_col=0)
    mgr = EnrichmentManager(de_results=de_df, species=species, output_dir=output_dir, theme=theme)
    mgr.run()
    echo(f"Enrichment analysis completed. Results in {output_dir}")
