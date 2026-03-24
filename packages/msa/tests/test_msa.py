import shutil
from pathlib import Path
import pytest
from unittest.mock import MagicMock

from bio_analyze_msa.aligners import MafftAligner, MuscleAligner, PythonAligner
from bio_analyze_msa.tree import DistanceTreeBuilder, FastTreeBuilder

@pytest.fixture
def sample_fasta():
    return Path(__file__).parent / "data" / "sample.fasta"

@pytest.fixture
def sample_aligned_fasta():
    return Path(__file__).parent / "data" / "aligned_cli.fasta"

def test_mafft_aligner(monkeypatch, tmp_path, sample_fasta):
    monkeypatch.setattr("shutil.which", lambda x: "/fake/path/mafft")
    
    mock_res = MagicMock()
    mock_res.stdout = ">XP_035468649.2\nACGT\n"
    
    mock_run = MagicMock(return_value=mock_res)
    monkeypatch.setattr("bio_analyze_msa.aligners.mafft.run", mock_run)
    
    aligner = MafftAligner()
    output_file = tmp_path / "out.fasta"
    
    res = aligner.align(sample_fasta, output_file, auto=True)
    
    assert res.exists()
    assert res.read_text() == ">XP_035468649.2\nACGT\n"
    mock_run.assert_called_once()
    assert "--auto" in mock_run.call_args[0][0]

def test_muscle_aligner(monkeypatch, tmp_path, sample_fasta):
    monkeypatch.setattr("shutil.which", lambda x: "/fake/path/muscle")
    
    # Mock version check
    mock_res = MagicMock()
    mock_res.stdout = "MUSCLE v5.1\n"
    mock_res.stderr = ""
    
    mock_run = MagicMock(return_value=mock_res)
    monkeypatch.setattr("bio_analyze_msa.aligners.muscle.run", mock_run)
    
    aligner = MuscleAligner()
    output_file = tmp_path / "out.fasta"
    
    aligner.align(sample_fasta, output_file)
    
    assert mock_run.call_count == 2
    args = mock_run.call_args_list[1][0][0]
    assert "-align" in args

def test_python_aligner(tmp_path, sample_fasta):
    aligner = PythonAligner()
    output_file = tmp_path / "out.fasta"
    res = aligner.align(sample_fasta, output_file)
    
    assert res.exists()
    content = res.read_text()
    assert ">XP_035468649.2" in content
    assert ">BAD06253.1" in content
    assert ">Larimichthys" in content

def test_distance_tree(tmp_path, sample_aligned_fasta):
    builder = DistanceTreeBuilder()
    output_file = tmp_path / "tree.nwk"
    
    res = builder.build(sample_aligned_fasta, output_file, method="upgma")
    assert res.exists()
    content = res.read_text()
    assert "XP_035468649.2" in content

def test_fasttree_builder(monkeypatch, tmp_path, sample_aligned_fasta):
    monkeypatch.setattr("shutil.which", lambda x: "/fake/path/fasttree")
    
    mock_res = MagicMock()
    mock_res.stdout = "(XP_035468649.2:0.1,BAD06253.1:0.2,Larimichthys:0.3);\n"
    
    mock_run = MagicMock(return_value=mock_res)
    monkeypatch.setattr("bio_analyze_msa.tree.fasttree.run", mock_run)
    
    builder = FastTreeBuilder()
    output_file = tmp_path / "tree.nwk"
    
    res = builder.build(sample_aligned_fasta, output_file, nt=True)
    
    assert res.exists()
    assert "XP_035468649.2:0.1" in res.read_text()
    mock_run.assert_called_once()
    assert "-nt" in mock_run.call_args[0][0]
