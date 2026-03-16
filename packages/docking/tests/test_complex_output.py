import importlib.util
import shutil
from pathlib import Path

import pytest
from bio_analyze_docking.engine import DockingEngine
from bio_analyze_docking.nodes import DockingNode

from bio_analyze_core.pipeline import Context

# Check optional dependencies safely
try:
    import vina
    HAS_VINA = True
except ImportError:
    HAS_VINA = False

try:
    import pymol
    HAS_PYMOL = True
except ImportError:
    HAS_PYMOL = False

# Define paths relative to the package root
DATA_DIR = Path(__file__).parent / "data"
RECEPTOR_DIR = DATA_DIR / "receptor"
LIGAND_DIR = DATA_DIR / "ligand"
PREPARED_RECEPTOR_DIR = DATA_DIR / "prepared_receptor"
PREPARED_LIGAND_DIR = DATA_DIR / "prepared_ligand"


@pytest.fixture
def real_test_data(tmp_path):
    # Use real prepared data if available, otherwise skip or fail
    if not PREPARED_RECEPTOR_DIR.exists() or not PREPARED_LIGAND_DIR.exists():
        pytest.skip("Prepared data directory not found")

    pdbqt_receptors = list(PREPARED_RECEPTOR_DIR.glob("*.pdbqt"))
    pdbqt_ligands = list(PREPARED_LIGAND_DIR.glob("*.pdbqt"))

    if not pdbqt_receptors or not pdbqt_ligands:
        pytest.skip("Test prepared data missing")

    rec_pdbqt_src = pdbqt_receptors[0]
    lig_pdbqt_src = pdbqt_ligands[0]

    rec_pdbqt = tmp_path / "receptor.pdbqt"
    lig_pdbqt = tmp_path / "ligand.pdbqt"

    shutil.copy(rec_pdbqt_src, rec_pdbqt)
    shutil.copy(lig_pdbqt_src, lig_pdbqt)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    return rec_pdbqt, lig_pdbqt, output_dir


@pytest.mark.skipif(not HAS_VINA, reason="Vina python package not installed")
@pytest.mark.skipif(not HAS_PYMOL, reason="PyMOL python package not installed")
def test_save_complexes(real_test_data):
    rec_file, lig_file, output_dir = real_test_data

    # Initialize Engine (VinaEngine)
    engine = DockingEngine(rec_file, lig_file, output_dir)

    # We must run docking to get results
    # Use small box around the ligand (if we knew where it is) or auto-box
    from bio_analyze_docking.prep import get_box_from_ligand
    
    # Use ligand for box to ensure Vina finds a pose quickly
    center, size = get_box_from_ligand(lig_file, padding=4.0)
    
    engine.compute_box(center, size)
    engine.dock(exhaustiveness=1, n_poses=1) # Fast docking

    # Save complexes
    engine.save_complexes(n_complexes=1, output_dir=output_dir, output_name_prefix="complex_test")

    # Check if output exists
    # VinaEngine uses PyMOL to save PDB
    # expected_file = output_dir / "complex_test_1.pdb"
    # Or maybe just complex_test.pdb if n=1?
    # Usually it appends index if multiple, but let's check implementation behavior or just list dir
    # Based on merge_complex_with_pymol logic (not visible here but implied), it probably names them with index.

    files = list(output_dir.glob("complex_test*.pdb"))
    assert len(files) > 0, "No complex PDB files generated"


@pytest.mark.skipif(not HAS_VINA, reason="Vina python package not installed")
@pytest.mark.skipif(not HAS_PYMOL, reason="PyMOL python package not installed")
def test_docking_node_complex_output(real_test_data):
    rec_file, lig_file, output_dir = real_test_data

    from unittest.mock import MagicMock

    context = Context()
    context["rec_key"] = str(rec_file)
    context["lig_key"] = str(lig_file)

    node = DockingNode(
        receptor_key="rec_key",
        ligand_key="lig_key",
        output_dir=output_dir,
        center=None,
        autobox_ligand=lig_file, # Use ligand to box
        padding=4.0,
        exhaustiveness=1,
        n_poses=1,
        output_docked_lig_recep_struct=True,
        n_docked_lig_recep_struct=1,
    )

    # We mock progress/logger but use real engine
    progress = MagicMock()
    logger = MagicMock()

    node.run(context, progress, logger)

    # Check results
    results = context.get("docking_results", [])
    assert len(results) == 1
    assert results[0]["status"] == "success"

    # Check output files
    # DockingNode saves complexes in output_dir / "dock_results" / "complex" / rec_stem
    rec_stem = rec_file.stem
    complex_dir = output_dir / "dock_results" / "complex" / rec_stem

    assert complex_dir.exists()
    files = list(complex_dir.glob("*.pdb"))
    assert len(files) > 0
