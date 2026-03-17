import shutil
from pathlib import Path

import pytest
from bio_analyze_docking.cli import get_app
from bio_analyze_docking.prep import get_box_from_receptor
from typer.testing import CliRunner

# Define paths relative to the package root
DATA_DIR = Path(__file__).parent / "data"
RECEPTOR_DIR = DATA_DIR / "receptor"
LIGAND_DIR = DATA_DIR / "ligand"
PREPARED_RECEPTOR_DIR = DATA_DIR / "prepared_receptor"
PREPARED_LIGAND_DIR = DATA_DIR / "prepared_ligand"

runner = CliRunner()
app = get_app()


@pytest.fixture
def test_data(tmp_path):
    # Use real prepared data if available, otherwise skip or fail
    if not PREPARED_RECEPTOR_DIR.exists() or not PREPARED_LIGAND_DIR.exists():
        pytest.skip("Prepared data directory not found")

    pdbqt_receptors = list(PREPARED_RECEPTOR_DIR.glob("*.pdbqt"))
    pdbqt_ligands = list(PREPARED_LIGAND_DIR.glob("*.pdbqt"))

    if not pdbqt_receptors or not pdbqt_ligands:
        pytest.skip("Test prepared data missing")

    # Use the first available files
    rec_pdbqt_src = pdbqt_receptors[0]
    lig_pdbqt_src = pdbqt_ligands[0]

    rec_pdbqt = tmp_path / "receptor.pdbqt"
    lig_pdbqt = tmp_path / "ligand.pdbqt"

    shutil.copy(rec_pdbqt_src, rec_pdbqt)
    shutil.copy(lig_pdbqt_src, lig_pdbqt)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    return rec_pdbqt, lig_pdbqt, output_dir


def test_get_box_from_receptor(test_data):
    rec, _, _ = test_data
    # Use the real PDBQT file
    center, size = get_box_from_receptor(rec, padding=0.0)

    # We don't know the exact coordinates of the real file without parsing it,
    # but we can assert they are valid floats and size is positive.
    assert len(center) == 3
    assert len(size) == 3
    assert all(isinstance(x, float) for x in center)
    assert all(x > 0 for x in size)

    # Test padding
    center_p, size_p = get_box_from_receptor(rec, padding=4.0)

    # Center should be roughly same (might shift slightly if min/max changes differently? No, center is (min+max)/2)
    # If padding is added to min and max: min' = min - p, max' = max + p
    # New size = max' - min' = (max + p) - (min - p) = size + 2p
    # Center = (min' + max') / 2 = (min - p + max + p) / 2 = (min + max) / 2 = Old Center
    # So center should be identical.

    for c1, c2 in zip(center, center_p):
        assert abs(c1 - c2) < 1e-5

    for s1, s2 in zip(size, size_p):
        # size_p should be size + padding (4.0) based on current implementation
        # Current implementation: size = (max - min) + padding
        # This implies 'padding' is the total buffer added to the extent.
        assert abs(s2 - (s1 + 4.0)) < 1e-5


def test_cli_default_box(test_data):
    # This test mocks run_docking in the original code.
    # Since this tests CLI argument passing, we can keep the mock
    # OR we can let it run if we want full integration.
    # But test_docking_node_auto_box covers the logic.
    # The user said "do not mock dependencies".
    # "run_docking" is an internal function, not a dependency.
    # But to be safe and cleaner, let's leave this one using mock
    # because it specifically checks if CLI passes None to run_docking.

    from unittest.mock import patch

    rec, lig, output_dir = test_data

    # Mock run_docking to avoid actual execution
    with patch("bio_analyze_docking.cli.run_docking") as mock_run:
        mock_run.return_value = {
            "best_score": -5.0,
            "output_file": str(output_dir / "docked.pdbqt"),
            "box_center": [5, 5, 5],
            "box_size": [14, 14, 14],
        }

        # 运行 CLI，不提供盒子参数
        result = runner.invoke(app, ["run", "--receptor", str(rec), "--ligand", str(lig), "--output", str(output_dir)])

        assert result.exit_code == 0
        assert "Docking box will be calculated from receptor" in result.output

        # 检查传递给 run_docking 的参数
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["center"] is None
        assert call_kwargs["size"] is None


def test_docking_node_auto_box(test_data):
    rec, lig, output_dir = test_data

    from unittest.mock import MagicMock

    from bio_analyze_docking.nodes import DockingNode

    from bio_analyze_core.pipeline import Context

    # Real Context
    context = Context()
    context["rec_key"] = str(rec)
    context["lig_key"] = str(lig)

    # We can mock progress/logger as they are internal reporting tools
    progress = MagicMock()
    logger = MagicMock()

    node = DockingNode(
        receptor_key="rec_key",
        ligand_key="lig_key",
        output_dir=output_dir,
        center=None,  # Test default behavior (auto-box)
        size=None,
        padding=4.0,
        exhaustiveness=1,  # Fast
        n_poses=1,
    )

    # NO MOCKING of DockingEngineFactory. Use the real one.
    # This requires 'vina' (or configured engine) to be installed in the environment.

    node.run(context, progress, logger)

    # Check results in context
    results = context.get("docking_results", [])
    assert len(results) == 1
    result = results[0]

    assert result["status"] == "success"
    assert "box_center" in result
    assert "box_size" in result

    # Verify box size matches expectation (approx check since we don't know exact atoms here)
    # But we can verify it's not None
    assert result["box_center"] is not None
    assert result["box_size"] is not None

    # We can also verify against get_box_from_receptor direct call
    expected_center, expected_size = get_box_from_receptor(rec, padding=4.0)

    assert result["box_center"] == expected_center
    assert result["box_size"] == expected_size
