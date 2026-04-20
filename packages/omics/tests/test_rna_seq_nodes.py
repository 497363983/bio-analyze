"""Tests for RNA-Seq pipeline nodes."""

from unittest.mock import MagicMock

from bio_analyze_core.pipeline import Context
from bio_analyze_omics.rna_seq.nodes import _recover_reference_info


def test_recover_reference_info_fills_missing_gtf_from_reference_dir(tmp_path):
    ref_dir = tmp_path / "reference" / "ASM1334776v1" / "nested"
    ref_dir.mkdir(parents=True)
    fasta = tmp_path / "reference" / "ASM1334776v1" / "ASM1334776v1.fa"
    gtf_gz = ref_dir / "Scophthalmus_maximus.ASM1334776v1.115.gtf.gz"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")
    gtf_gz.write_text("gtf-placeholder", encoding="utf-8")

    context = Context(
        output_dir=tmp_path,
        assembly="ASM1334776v1",
        species="Scophthalmus maximus",
        genome_fasta=None,
        genome_gtf=None,
    )
    logger = MagicMock()

    ref_info = _recover_reference_info(
        context,
        {"fasta": fasta, "gtf": None},
        logger,
        "quantification",
    )

    assert ref_info["fasta"] == fasta
    assert ref_info["gtf"] == gtf_gz
    logger.warning.assert_not_called()
