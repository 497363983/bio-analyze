from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from bio_analyze_rna_seq.quant import QuantManager


@pytest.fixture
def mock_quant_manager(tmp_path):
    output_dir = tmp_path / "quant_output"
    output_dir.mkdir()

    reads = {"sample1": {"R1": Path("sample1_R1.fq"), "R2": Path("sample1_R2.fq")}}
    reference = {"fasta": Path("genome.fa"), "gtf": Path("genome.gtf")}

    return QuantManager(reads, reference, output_dir)


@patch("bio_analyze_rna_seq.quant.run_command")
@patch("shutil.which")
def test_quant_manager_run(mock_which, mock_run, mock_quant_manager):
    mock_which.return_value = "/usr/bin/salmon"
    mock_run.return_value = MagicMock(returncode=0)

    # Mock _merge_counts to avoid reading non-existent files
    with patch.object(QuantManager, "_merge_counts") as mock_merge:
        mock_merge.return_value = pd.DataFrame({"sample1": [10, 20]}, index=["gene1", "gene2"])

        result = mock_quant_manager.run()

        assert isinstance(result, pd.DataFrame)
        assert mock_run.call_count >= 2  # Index + Quant
        assert mock_merge.called
