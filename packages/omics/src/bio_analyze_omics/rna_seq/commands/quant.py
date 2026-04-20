from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option, echo
from bio_analyze_core.i18n import _

from bio_analyze_omics.rna_seq.commands.utils import detect_clean_reads
from bio_analyze_omics.rna_seq.quant.framework import DEFAULT_QUANT_TOOL, QuantManager


def run_quant(
    input_dir: Path = Option(
        ..., "-i", "--input", help=_("Directory with clean FastQ files.")
    ),
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    fasta: Path = Option(
        ..., "--fasta", help=_("Genome/Transcriptome FASTA file.")
    ),
    gtf: Path = Option(
        None,
        "--gtf",
        help=_("Genome GTF file (optional if FASTA is transcriptome)."),
    ),
    tool: str = Option(
        DEFAULT_QUANT_TOOL,
        "--tool",
        help=(
            """Quantification tool name."""
        ),
    ),
    compare_tools: list[str] = Option(
        None,
        "--compare-tool",
        help=_("Optional comparison quantifiers, repeatable."),
    ),
    threads: int = Option(4, "-t", "--threads", help=_("Number of threads.")),
):
    """Run extensible transcript quantification. """
    reads = detect_clean_reads(input_dir)
    if not reads:
        echo(f"No clean reads found in {input_dir}", err=True)
        raise Exit(code=1)

    reference = {"fasta": fasta}
    if gtf:
        reference["gtf"] = gtf

    mgr = QuantManager(
        reads=reads,
        reference=reference,
        output_dir=output_dir,
        threads=threads,
        tool=tool,
        compare_tools=compare_tools or [],
    )
    mgr.run()
    echo(f"Quantification with {tool} completed. Results in {output_dir}")
