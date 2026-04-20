from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.align import StarAlignmentManager
from bio_analyze_omics.rna_seq.commands.utils import detect_clean_reads


def run_align(
    input_dir: Path = Option(
        ..., "-i", "--input", help=_("Directory with clean FastQ files.")
    ),
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    fasta: Path = Option(..., "--fasta", help=_("Genome FASTA file.")),
    gtf: Path = Option(None, "--gtf", help=_("Genome GTF file.")),
    threads: int = Option(4, "-t", "--threads", help=_("Number of threads.")),
    theme: str = Option("default", help=_("Plot theme.")),
):
    """Run STAR alignment. """
    reads = detect_clean_reads(input_dir)
    if not reads:
        echo(f"No clean reads found in {input_dir}", err=True)
        raise Exit(code=1)

    reference = {"fasta": fasta}
    if gtf:
        reference["gtf"] = gtf

    mgr = StarAlignmentManager(
        reads=reads, reference=reference, output_dir=output_dir, threads=threads, theme=theme
    )
    mgr.run()
    echo(f"Alignment completed. Results in {output_dir}")
