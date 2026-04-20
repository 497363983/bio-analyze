from __future__ import annotations

from pathlib import Path

import pandas as pd

from bio_analyze_core.cli.app import Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.de import DEManager


def run_de(
    counts: Path = Option(..., "--counts", help=_("Counts matrix CSV file.")),
    design: Path = Option(..., "--design", help=_("Design matrix CSV file.")),
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    theme: str = Option("default", help=_("Plot theme.")),
):
    """Run differential expression analysis (DESeq2). """
    counts_df = pd.read_csv(counts, index_col=0)
    mgr = DEManager(counts=counts_df, design_file=design, output_dir=output_dir, theme=theme)
    mgr.run()
    echo(f"DE analysis completed. Results in {output_dir}")
