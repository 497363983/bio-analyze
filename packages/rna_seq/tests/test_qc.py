from unittest.mock import MagicMock, patch

import pytest

from bio_analyze_rna_seq.qc import QCManager


@pytest.fixture
def mock_qc_manager(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Create dummy fastq files
    (input_dir / "sample1_R1.fastq.gz").touch()
    (input_dir / "sample1_R2.fastq.gz").touch()

    return QCManager(input_dir, output_dir, skip_trim=True)


@patch("bio_analyze_rna_seq.qc.run_command")
def test_qc_manager_run(mock_run, mock_qc_manager):
    # Mock subprocess run to avoid actual execution
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    cleaned_samples = mock_qc_manager.run()

    assert "sample1" in cleaned_samples
    assert "R1" in cleaned_samples["sample1"]
    assert "R2" in cleaned_samples["sample1"]
    # Check if fastp command was called (via subprocess.run wrapper)
    assert mock_run.called


def test_qc_detect_files(mock_qc_manager):
    files = mock_qc_manager._detect_files(mock_qc_manager.input_dir)
    assert "sample1" in files
    assert files["sample1"]["R1"].name == "sample1_R1.fastq.gz"
