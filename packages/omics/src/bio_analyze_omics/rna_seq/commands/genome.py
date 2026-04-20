from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Exit, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.commands.utils import search_and_select_reference
from bio_analyze_omics.rna_seq.genome import GenomeManager


def prepare_genome(
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    species: str = Option(None, "-s", "--species", help=_("Species name.")),
    assembly: str = Option(
        None,
        "--assembly",
        help=_("Reference assembly accession, e.g. GCA_013347765.1."),
    ),
    fasta: Path = Option(None, "--fasta", help=_("Genome FASTA file.")),
    gtf: Path = Option(None, "--gtf", help=_("Genome GTF file.")),
):
    """Prepare reference genome (download or index). """
    if not species and not assembly and not fasta:
        echo("Error: Either --species, --assembly, or --fasta must be provided.", err=True)
        raise Exit(code=1)

    provider = None
    if species and not assembly and not fasta:
        assembly, provider = search_and_select_reference(species)

    mgr = GenomeManager(
        species=species,
        assembly=assembly,
        provider=provider,
        fasta=fasta,
        gtf=gtf,
        output_dir=output_dir,
    )
    mgr.prepare()
    echo(f"Genome prepared in {output_dir}")
