from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_omics.rna_seq.qc import QCManager


def run_qc(
    input_dir: Path = Option(
        ..., "-i", "--input", help=_("Input directory (raw FastQ).")
    ),
    output_dir: Path = Option(..., "-o", "--output", help=_("Output directory.")),
    threads: int = Option(4, "-t", "--threads", help=_("Number of threads.")),
    skip_qc: bool = Option(False, help=_("Skip FastQC/fastp stats.")),
    skip_trim: bool = Option(False, help=_("Skip trimming.")),
    # QC Params
    qualified_quality_phred: int = Option(None, help=_("Phred quality threshold.")),
    unqualified_percent_limit: int = Option(
        None, help=_("Unqualified percent limit.")
    ),
    n_base_limit: int = Option(None, help=_("N base limit.")),
    length_required: int = Option(None, help=_("Length required.")),
    adapter_sequence: str = Option(None, help=_("Adapter sequence R1.")),
    adapter_sequence_r2: str = Option(None, help=_("Adapter sequence R2.")),
    dedup: bool = Option(False, help=_("Enable deduplication.")),
):
    """Run quality control and trimming. """
    mgr = QCManager(
        input_dir=input_dir,
        output_dir=output_dir,
        threads=threads,
        skip_qc=skip_qc,
        skip_trim=skip_trim,
        qualified_quality_phred=qualified_quality_phred,
        unqualified_percent_limit=unqualified_percent_limit,
        n_base_limit=n_base_limit,
        length_required=length_required,
        adapter_sequence=adapter_sequence,
        adapter_sequence_r2=adapter_sequence_r2,
        dedup=dedup,
    )
    mgr.run()
    echo(f"QC completed. Results in {output_dir}")
