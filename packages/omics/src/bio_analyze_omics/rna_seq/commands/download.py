from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.sra import SRAManager


def download_sra(
    sra_ids: list[str] = Argument(..., help=_("List of SRA Accession IDs.")),
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    threads: int = Option(4, "-t", "--threads", help=_("Number of threads.")),
):
    """Download FastQ files from SRA. """
    mgr = SRAManager(output_dir=output_dir, threads=threads)
    mgr.download(sra_ids)
    echo(f"Downloaded {len(sra_ids)} samples to {output_dir}")
