import sys
from unittest.mock import MagicMock

# Mock external dependencies that might be missing in the environment
sys.modules["vina"] = MagicMock()
sys.modules["gemmi"] = MagicMock()  # meeko dependency that might be missing

# sys.modules["meeko"] = MagicMock() # meeko might be installed, but mocking it is safe if we don't test its logic
# sys.modules["rdkit"] = MagicMock() # same for rdkit

# We only mock vina because it's the one causing build issues.
# If meeko/rdkit are installed, we can use them. If not, we might need to mock them too.
# Given I commented out vina, meeko and rdkit should be installed.
# But just in case, let's wrap imports.

import pytest


def test_import_rna_seq_pipeline():
    try:
        from bio_analyze_omics.rna_seq.pipeline import RNASeqPipeline

        assert RNASeqPipeline is not None
    except ImportError as e:
        pytest.fail(f"Failed to import bio_analyze_omics.rna_seq.pipeline: {e}")


def test_import_docking_api():
    try:
        from bio_analyze_docking.api import run_docking

        assert run_docking is not None
    except ImportError as e:
        pytest.fail(f"Failed to import bio_analyze_docking.api: {e}")


def test_instantiate_rna_seq_pipeline(tmp_path):
    try:
        from bio_analyze_omics.rna_seq.pipeline import RNASeqPipeline
    except ImportError:
        pytest.skip("bio_analyze_omics not installed")

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    design_file = tmp_path / "design.csv"
    design_file.touch()

    pipeline = RNASeqPipeline(input_dir=input_dir, output_dir=output_dir, design_file=design_file)
    assert pipeline.input_dir == input_dir
    assert pipeline.output_dir == output_dir


def test_docking_pipeline_construction(tmp_path, monkeypatch):
    try:
        from bio_analyze_docking import api
    except ImportError:
        pytest.skip("bio_analyze_docking not installed")

    # Mock nodes to avoid actual execution logic
    monkeypatch.setattr(api, "ReceptorPrepNode", MagicMock())
    monkeypatch.setattr(api, "LigandPrepNode", MagicMock())
    monkeypatch.setattr(api, "DockingNode", MagicMock())

    # Mock Pipeline.run to avoid execution
    # We need to mock bio_analyze_core.pipeline.Pipeline.run
    # Since api imports Pipeline from bio_analyze_core.pipeline, we can mock it there

    mock_run = MagicMock()
    monkeypatch.setattr("bio_analyze_core.pipeline.Pipeline.run", mock_run)

    receptor = tmp_path / "receptor.pdbqt"
    ligand = tmp_path / "ligand.pdbqt"
    output_dir = tmp_path / "docking_out"

    try:
        api.run_docking(receptor, ligand, output_dir)
    except RuntimeError as e:
        # Expected because we didn't mock the context result retrieval
        assert "Docking pipeline finished but no result found" in str(e)

    # Verify run was called
    assert mock_run.called


def test_docking_batch_pipeline_construction(tmp_path, monkeypatch):
    try:
        from bio_analyze_docking import api
    except ImportError:
        pytest.skip("bio_analyze_docking not installed")

    # Mock nodes
    monkeypatch.setattr(api, "BatchReceptorPrepNode", MagicMock())
    monkeypatch.setattr(api, "BatchLigandPrepNode", MagicMock())
    monkeypatch.setattr(api, "BatchDockingNode", MagicMock())

    # Mock Pipeline.run
    mock_run = MagicMock()
    monkeypatch.setattr("bio_analyze_core.pipeline.Pipeline.run", mock_run)

    receptors = [tmp_path / "rec1.pdb", tmp_path / "rec2.pdb"]
    ligands = [tmp_path / "lig1.sdf", tmp_path / "lig2.sdf"]
    output_dir = tmp_path / "batch_out"

    try:
        api.run_docking_batch(receptors, ligands, output_dir)
    except Exception:
        # It might fail getting results from context, which is expected
        pass

    assert mock_run.called
