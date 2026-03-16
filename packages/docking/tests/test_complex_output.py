from unittest.mock import MagicMock, patch

import pytest
from bio_analyze_docking.engines import DockingEngineFactory
from bio_analyze_docking.nodes import DockingNode

from bio_analyze_core.pipeline import Context


@pytest.fixture
def mock_vina(monkeypatch):
    # Mock Vina class
    mock_instance = MagicMock()
    # Setup energies return value
    # list of [affinity, rmsd_lb, rmsd_ub]
    mock_instance.energies.return_value = [[-9.0, 0, 0], [-8.0, 1, 2]]

    mock_cls = MagicMock(return_value=mock_instance)
    
    # We need to mock where Vina is imported/used.
    # In bio_analyze_docking.engine, Vina is imported from vina.
    # But since we mock sys.modules['vina'] globally in other tests (or here if needed),
    # we should check how DockingEngine uses it.
    
    # Assuming DockingEngine imports Vina from vina package directly or via engines.vina
    # Let's mock sys.modules["vina"] if not already mocked
    import sys
    if "vina" not in sys.modules or not isinstance(sys.modules["vina"], MagicMock):
        sys.modules["vina"] = MagicMock()
        
    sys.modules["vina"].Vina = mock_cls

    return mock_instance


@pytest.fixture
def mock_pymol(monkeypatch):
    mock_cmd = MagicMock()
    # count_states return 2 states
    mock_cmd.count_states.return_value = 2
    # Mock cmd in bio_analyze_docking.utils because that's where merge_complex_with_pymol uses it
    monkeypatch.setattr("bio_analyze_docking.utils.cmd", mock_cmd)
    return mock_cmd


def test_save_complexes(tmp_path, mock_vina, mock_pymol):
    # Create dummy receptor and ligand files
    rec_file = tmp_path / "receptor.pdbqt"
    rec_file.write_text("ATOM      1  N   MET A   1      27.640  32.414   3.707  1.00 10.00     0.163 HD\n")

    lig_file = tmp_path / "ligand.pdbqt"
    lig_file.write_text("ATOM      1  C   LIG A   1      10.000  10.000  10.000  1.00  0.00     0.000 C \n")

    output_dir = tmp_path / "output"

    # Initialize Engine via Factory or direct class if needed, but test uses DockingEngine alias
    # DockingEngine is VinaEngine
    from bio_analyze_docking.engine import DockingEngine
    engine = DockingEngine(rec_file, lig_file, output_dir)

    # Test saving all complexes
    engine.save_complexes()

    # Verify PyMOL calls
    assert mock_pymol.reinitialize.call_count >= 2  # start and finally
    mock_pymol.load.assert_any_call(str(rec_file), "receptor")
    mock_pymol.create.assert_any_call("complex_1", "receptor or (ligand_poses and state 1)")
    mock_pymol.save.assert_any_call(str(output_dir / "complex_pose_1.pdb"), "complex_1")

    # Test saving top 1 complex
    mock_pymol.reset_mock()
    engine.save_complexes(n_complexes=1)
    mock_pymol.save.assert_called_once()
    assert "complex_pose_1.pdb" in mock_pymol.save.call_args[0][0]


def test_docking_node_complex_output(tmp_path, mock_vina):
    rec_file = tmp_path / "receptor.pdbqt"
    rec_file.touch()
    lig_file = tmp_path / "ligand.pdbqt"
    lig_file.touch()

    output_dir = tmp_path / "output"

    node = DockingNode(
        receptor_key="rec",
        ligand_key="lig",
        output_dir=output_dir,
        center=[0, 0, 0],
        size=[20, 20, 20],
        output_docked_lig_recep_struct=True,
        n_docked_lig_recep_struct=1,
    )

    context = Context(storage_dir=tmp_path)
    context["rec"] = str(rec_file)
    context["lig"] = str(lig_file)

    # Mock engine methods called by Node
    # DockingNode calls DockingEngineFactory.create_engine
    with patch("bio_analyze_docking.nodes.DockingEngineFactory.create_engine") as MockCreate:
        instance = MockCreate.return_value
        instance.save_results.return_value = output_dir / "docked.pdbqt"
        instance.score.return_value = -9.0
        instance.get_all_poses_info.return_value = []

        node.run(context, MagicMock(), MagicMock())

        # Verify save_complexes was called with correct arg
        instance.save_complexes.assert_called_once_with(1)
