"""Tests for STAR alignment command construction."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from bio_analyze_omics.rna_seq.align import StarAlignmentManager


@pytest.fixture
def star_alignment_manager(tmp_path):
    output_dir = tmp_path / "align"
    star_index_dir = output_dir / "star_index"
    star_index_dir.mkdir(parents=True)
    (star_index_dir / "SA").touch()

    reads = {
        "sample1": {
            "R1": tmp_path / "sample1_R1.fastq.gz",
            "R2": tmp_path / "sample1_R2.fastq.gz",
        }
    }
    reads["sample1"]["R1"].touch()
    reads["sample1"]["R2"].touch()

    reference = {"fasta": tmp_path / "reference.fa"}
    reference["fasta"].touch()

    return StarAlignmentManager(
        reads=reads,
        reference=reference,
        output_dir=output_dir,
        star_index_dir=star_index_dir,
    )


@patch("bio_analyze_omics.rna_seq.align.shutil.rmtree")
@patch(
    "bio_analyze_omics.rna_seq.align.uuid.uuid4",
    return_value=SimpleNamespace(hex="fixedtmpdir"),
)
@patch("bio_analyze_omics.rna_seq.align.run_command")
def test_align_sample_uses_linux_tmp_dir(mock_run, mock_uuid, mock_rmtree, star_alignment_manager):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    bam_path = star_alignment_manager._align_sample(
        "sample1",
        star_alignment_manager.reads["sample1"],
        star_alignment_manager.output_dir / "sample1_",
    )

    first_call = mock_run.call_args_list[0]
    first_cmd = first_call.args[0]
    assert first_cmd[:2] == ["STAR", "--genomeDir"]
    assert "--outTmpDir" in first_cmd
    assert first_cmd[first_cmd.index("--outTmpDir") + 1] == "/tmp/bioanalyze_star_sample1_fixedtmpdir"

    second_call = mock_run.call_args_list[1]
    assert second_call.args[0] == ["samtools", "index", str(bam_path)]
    mock_uuid.assert_called_once()
    mock_rmtree.assert_called_once_with(
        Path("/tmp/bioanalyze_star_sample1_fixedtmpdir"),
        ignore_errors=True,
    )


@patch("bio_analyze_omics.rna_seq.align.shutil.rmtree")
@patch(
    "bio_analyze_omics.rna_seq.align.uuid.uuid4",
    return_value=SimpleNamespace(hex="fixedtmpdir"),
)
@patch("bio_analyze_omics.rna_seq.align.run_command")
def test_empty_existing_bam_triggers_realign(mock_run, mock_uuid, mock_rmtree, star_alignment_manager):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    bam_path = star_alignment_manager.output_dir / "sample1_Aligned.sortedByCoord.out.bam"
    bam_path.touch()

    result = star_alignment_manager._align_sample(
        "sample1",
        star_alignment_manager.reads["sample1"],
        star_alignment_manager.output_dir / "sample1_",
    )

    assert result == bam_path
    assert not bam_path.exists()
    first_cmd = mock_run.call_args_list[0].args[0]
    assert first_cmd[:2] == ["STAR", "--genomeDir"]
    mock_uuid.assert_called_once()
    mock_rmtree.assert_called_once_with(
        Path("/tmp/bioanalyze_star_sample1_fixedtmpdir"),
        ignore_errors=True,
    )


@patch("bio_analyze_omics.rna_seq.align.uuid.uuid4")
@patch("bio_analyze_omics.rna_seq.align.run_command")
def test_existing_bam_without_index_gets_indexed(mock_run, mock_uuid, star_alignment_manager):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    bam_path = star_alignment_manager.output_dir / "sample1_Aligned.sortedByCoord.out.bam"
    bam_path.write_bytes(b"BAM")

    result = star_alignment_manager._align_sample(
        "sample1",
        star_alignment_manager.reads["sample1"],
        star_alignment_manager.output_dir / "sample1_",
    )

    assert result == bam_path
    assert mock_run.call_args_list[0].args[0] == ["samtools", "quickcheck", str(bam_path)]
    assert mock_run.call_args_list[1].args[0] == ["samtools", "index", str(bam_path)]
    mock_uuid.assert_not_called()


@patch("bio_analyze_omics.rna_seq.align.shutil.rmtree")
@patch(
    "bio_analyze_omics.rna_seq.align.uuid.uuid4",
    return_value=SimpleNamespace(hex="fixedtmpdir"),
)
@patch("bio_analyze_omics.rna_seq.align.run_command")
def test_align_sample_cleans_tmp_dir_on_failure(
    mock_run,
    mock_uuid,
    mock_rmtree,
    star_alignment_manager,
):
    mock_run.side_effect = RuntimeError("STAR failed")

    with pytest.raises(RuntimeError, match="STAR failed"):
        star_alignment_manager._align_sample(
            "sample1",
            star_alignment_manager.reads["sample1"],
            star_alignment_manager.output_dir / "sample1_",
        )

    mock_uuid.assert_called_once()
    mock_rmtree.assert_called_once_with(
        Path("/tmp/bioanalyze_star_sample1_fixedtmpdir"),
        ignore_errors=True,
    )
