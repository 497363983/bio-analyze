from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from bio_analyze_rna_seq.de import DEManager


@pytest.fixture
def mock_de_manager(tmp_path):
    output_dir = tmp_path / "de_output"
    output_dir.mkdir()

    counts = pd.DataFrame(
        {
            "S1": [100, 200, 300],
            "S2": [110, 190, 310],
            "S3": [1000, 2000, 3000],  # Different condition
            "S4": [1100, 1900, 3100],
        },
        index=["gene1", "gene2", "gene3"],
    )

    design_file = tmp_path / "design.csv"
    pd.DataFrame(
        {
            "sample": ["S1", "S2", "S3", "S4"],
            "condition": ["Control", "Control", "Treated", "Treated"],
        }
    ).to_csv(design_file, index=False)

    return DEManager(counts, design_file, output_dir)


@patch("bio_analyze_rna_seq.de.DeseqDataSet")
@patch("bio_analyze_rna_seq.de.DeseqStats")
def test_de_manager_run(mock_stats, mock_dds, mock_de_manager):
    # Mock PyDESeq2 objects
    mock_dds_instance = MagicMock()
    mock_dds.return_value = mock_dds_instance

    mock_stats_instance = MagicMock()
    mock_stats_instance.results_df = pd.DataFrame(
        {"log2FoldChange": [2.0, -1.0, 0.5], "padj": [0.01, 0.04, 0.5]},
        index=["gene1", "gene2", "gene3"],
    )
    mock_stats.return_value = mock_stats_instance

    results = mock_de_manager.run()

    assert isinstance(results, pd.DataFrame)
    assert "log2FoldChange" in results.columns
    assert mock_dds_instance.deseq2.called
    assert mock_stats_instance.summary.called
