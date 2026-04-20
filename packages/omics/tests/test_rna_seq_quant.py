import gzip
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from bio_analyze_omics.rna_seq.quant.framework import (
    QuantManager,
    QuantRunResult,
    compare_quant_results,
    discover_alignment_bams,
    list_available_quantifiers,
)


@pytest.fixture
def mock_quant_manager(tmp_path):
    output_dir = tmp_path / "quant_output"
    output_dir.mkdir()

    reads = {"sample1": {"R1": Path("sample1_R1.fq"), "R2": Path("sample1_R2.fq")}}
    reference = {"fasta": Path("genome.fa"), "gtf": Path("genome.gtf")}

    return QuantManager(reads, reference, output_dir)


@patch("bio_analyze_omics.rna_seq.quant.framework.run_command")
@patch("shutil.which")
def test_quant_manager_run(mock_which, mock_run, mock_quant_manager):
    mock_which.return_value = "/usr/bin/salmon"
    mock_run.return_value = MagicMock(returncode=0)

    with patch(
        "bio_analyze_omics.rna_seq.quant.engines.salmon.SalmonQuantifier.merge_quantifications"
    ) as mock_merge:
        mock_merge.return_value = (
            pd.DataFrame({"sample1": [10, 20]}, index=["gene1", "gene2"]),
            {"tpm": pd.DataFrame({"sample1": [1.0, 2.0]}, index=["gene1", "gene2"])},
        )
        result = mock_quant_manager.run()
        result = mock_quant_manager.run()

        assert isinstance(result, pd.DataFrame)
    assert mock_merge.called


@patch("bio_analyze_omics.rna_seq.quant.framework.run_command")
@patch("shutil.which")
def test_build_index_decompresses_gtf_gz(mock_which, mock_run, tmp_path):
    output_dir = tmp_path / "quant_output"
    output_dir.mkdir()
    reads = {"sample1": {"R1": Path("sample1_R1.fq"), "R2": Path("sample1_R2.fq")}}
    fasta = tmp_path / "genome.fa"
    gtf_gz = tmp_path / "genome.gtf.gz"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")
    with gzip.open(gtf_gz, "wt", encoding="utf-8") as handle:
        handle.write("chr1\ttest\tgene\n")

    mock_which.side_effect = lambda name: f"/usr/bin/{name}" if name in {"salmon", "gffread"} else None
    mock_run.return_value = MagicMock(returncode=0)

    manager = QuantManager(reads, {"fasta": fasta, "gtf": gtf_gz}, output_dir)
    manager._build_index()

    prepared_gtf = output_dir / "genome.gtf"
    assert prepared_gtf.exists()
    gffread_cmd = mock_run.call_args_list[0].args[0]
    salmon_cmd = mock_run.call_args_list[1].args[0]
    assert gffread_cmd == ["gffread", "-w", str(output_dir / "transcripts.fa"), "-g", str(fasta), str(prepared_gtf)]
    assert salmon_cmd[:2] == ["salmon", "index"]


@patch("shutil.which")
def test_build_index_requires_gtf_and_gffread(mock_which, tmp_path):
    output_dir = tmp_path / "quant_output"
    output_dir.mkdir()
    reads = {"sample1": {"R1": Path("sample1_R1.fq"), "R2": Path("sample1_R2.fq")}}
    fasta = tmp_path / "genome.fa"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")

    mock_which.side_effect = lambda name: "/usr/bin/salmon" if name == "salmon" else None

    manager_missing_gtf = QuantManager(reads, {"fasta": fasta, "gtf": None}, output_dir)
    with pytest.raises(RuntimeError, match="Reference GTF is required"):
        manager_missing_gtf._build_index()

    manager_missing_gffread = QuantManager(reads, {"fasta": fasta, "gtf": tmp_path / "genome.gtf"}, output_dir)
    with pytest.raises(RuntimeError, match="gffread not found"):
        manager_missing_gffread._build_index()


@patch("bio_analyze_omics.rna_seq.quant.framework.run_command")
@patch("shutil.which")
def test_build_index_skips_when_complete_index_exists(mock_which, mock_run, tmp_path):
    output_dir = tmp_path / "quant_output"
    index_dir = output_dir / "salmon_index"
    index_dir.mkdir(parents=True)
    (index_dir / "versionInfo.json").write_text("{}", encoding="utf-8")
    reads = {"sample1": {"R1": Path("sample1_R1.fq"), "R2": Path("sample1_R2.fq")}}
    fasta = tmp_path / "genome.fa"
    gtf = tmp_path / "genome.gtf"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")
    gtf.write_text("chr1\ttest\tgene\n", encoding="utf-8")

    mock_which.side_effect = lambda name: f"/usr/bin/{name}" if name in {"salmon", "gffread"} else None

    manager = QuantManager(reads, {"fasta": fasta, "gtf": gtf}, output_dir)
    manager._build_index()

    mock_run.assert_not_called()


@patch("bio_analyze_omics.rna_seq.quant.framework.run_command")
@patch("shutil.which")
def test_build_index_rebuilds_incomplete_index(mock_which, mock_run, tmp_path):
    output_dir = tmp_path / "quant_output"
    index_dir = output_dir / "salmon_index"
    index_dir.mkdir(parents=True)
    (index_dir / "ref_indexing.log").write_text("partial", encoding="utf-8")
    reads = {"sample1": {"R1": Path("sample1_R1.fq"), "R2": Path("sample1_R2.fq")}}
    fasta = tmp_path / "genome.fa"
    gtf = tmp_path / "genome.gtf"
    fasta.write_text(">chr1\nACGT\n", encoding="utf-8")
    gtf.write_text("chr1\ttest\tgene\n", encoding="utf-8")

    mock_which.side_effect = lambda name: f"/usr/bin/{name}" if name in {"salmon", "gffread"} else None
    mock_run.return_value = MagicMock(returncode=0)

    manager = QuantManager(reads, {"fasta": fasta, "gtf": gtf}, output_dir)
    manager._build_index()

    assert not (index_dir / "ref_indexing.log").exists()
    gffread_cmd = mock_run.call_args_list[0].args[0]
    salmon_cmd = mock_run.call_args_list[1].args[0]
    assert gffread_cmd[:2] == ["gffread", "-w"]
    assert salmon_cmd[:2] == ["salmon", "index"]


def test_quant_framework_lists_expected_plugins():
    available = set(list_available_quantifiers())
    assert {"salmon", "kallisto", "featurecounts", "htseq-count", "rsem"} <= available


def test_compare_quant_results_builds_correlation_table(tmp_path):
    manager = QuantManager(
        reads={"sample1": {"R1": tmp_path / "sample1_R1.fq", "R2": tmp_path / "sample1_R2.fq"}},
        reference={"fasta": tmp_path / "genome.fa", "gtf": tmp_path / "genes.gtf"},
        output_dir=tmp_path / "quant_output",
    )
    left = manager.output_dir / "left"
    right = manager.output_dir / "right"
    left.mkdir(parents=True)
    right.mkdir(parents=True)

    left_result = QuantRunResult(
        tool="salmon",
        output_dir=left,
        counts_matrix=pd.DataFrame({"sample1": [1, 2]}, index=["gene1", "gene2"]),
    )
    right_result = QuantRunResult(
        tool="featurecounts",
        output_dir=right,
        counts_matrix=pd.DataFrame({"sample1": [1, 2]}, index=["gene1", "gene2"]),
    )

    comparison = compare_quant_results({"salmon": left_result, "featurecounts": right_result})
    assert {"left_tool", "right_tool", "pearson"} == set(comparison.columns)
    assert len(comparison) == 4


def test_quant_manager_writes_comparison_table_with_compare_tools(tmp_path):
    output_dir = tmp_path / "quant_output"
    output_dir.mkdir()
    manager = QuantManager(
        reads={"sample1": {"R1": tmp_path / "sample1_R1.fq", "R2": tmp_path / "sample1_R2.fq"}},
        reference={"fasta": tmp_path / "genome.fa", "gtf": tmp_path / "genes.gtf"},
        output_dir=output_dir,
        tool="salmon",
        compare_tools=["kallisto"],
    )

    primary_result = QuantRunResult(
        tool="salmon",
        output_dir=output_dir,
        counts_matrix=pd.DataFrame({"sample1": [1, 2]}, index=["gene1", "gene2"]),
    )
    compare_dir = output_dir / "comparisons" / "kallisto"
    compare_dir.mkdir(parents=True)
    compare_result = QuantRunResult(
        tool="kallisto",
        output_dir=compare_dir,
        counts_matrix=pd.DataFrame({"sample1": [1, 3]}, index=["gene1", "gene2"]),
    )
    primary_quantifier = MagicMock()
    primary_quantifier.run.return_value = primary_result
    compare_quantifier = MagicMock()
    compare_quantifier.run.return_value = compare_result

    with patch.object(
        QuantManager,
        "_create_quantifier",
        side_effect=[primary_quantifier, compare_quantifier],
    ) as mock_create:
        counts = manager.run()

    assert counts.equals(primary_result.counts_matrix)
    assert (output_dir / "tool_comparison.csv").exists()
    comparison = manager.get_comparison_table()
    assert comparison is not None
    assert set(comparison["left_tool"]) == {"salmon", "kallisto"}
    assert set(comparison["right_tool"]) == {"salmon", "kallisto"}

    compare_call = mock_create.call_args_list[1]
    assert compare_call.args[0] == "kallisto"
    assert compare_call.args[1] == compare_dir


def test_discover_alignment_bams_filters_requested_samples(tmp_path):
    align_dir = tmp_path / "align"
    align_dir.mkdir()
    sample1_bam = align_dir / "sample1_Aligned.sortedByCoord.out.bam"
    sample2_bam = align_dir / "sample2_Aligned.sortedByCoord.out.bam"
    sample1_bam.write_text("bam1", encoding="utf-8")
    sample2_bam.write_text("bam2", encoding="utf-8")

    alignments = discover_alignment_bams(align_dir, ["sample2"])

    assert alignments == {"sample2": sample2_bam}
