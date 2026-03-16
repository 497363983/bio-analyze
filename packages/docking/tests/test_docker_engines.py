import shutil
import subprocess
from pathlib import Path
import pytest
from bio_analyze_docking.api import run_docking

# Define paths relative to the package root
DATA_DIR = Path(__file__).parent / "data"
RECEPTOR_DIR = DATA_DIR / "receptor"
LIGAND_DIR = DATA_DIR / "ligand"

OUTPUT_DIR = Path(__file__).parent / "output"

@pytest.mark.skipif(not shutil.which("smina"), reason="Smina not installed")
def test_smina_executable():
    """Test if smina binary is executable and returns help."""
    result = subprocess.run(["smina", "--help"], capture_output=True, text=True)
    # Smina returns 0 or 1 depending on version when help is invoked, but usually prints help
    # Some versions print to stderr, some to stdout
    assert result.returncode in [0, 1]
    output = (result.stdout + result.stderr).lower()
    assert "smina" in output or "receptor" in output or "ligand" in output

@pytest.mark.skipif(not shutil.which("gnina"), reason="Gnina not installed")
def test_gnina_executable():
    """Test if gnina binary is executable and returns help."""
    result = subprocess.run(["gnina", "--help"], capture_output=True, text=True)
    assert result.returncode in [0, 1]
    output = (result.stdout + result.stderr).lower()
    assert "gnina" in output or "receptor" in output or "cnn" in output

@pytest.mark.skipif(not shutil.which("smina"), reason="Smina not installed")
def test_smina_docking_pipeline(tmp_path):
    """Test full docking pipeline with Smina using real data."""
    # Find input files
    receptor_file = list(RECEPTOR_DIR.glob("*.cif"))[0]
    ligand_file = list(LIGAND_DIR.glob("*.sdf"))[0]
    
    # Use persistent output directory
    output_dir = OUTPUT_DIR / "smina"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run docking
    result = run_docking(
        receptor=receptor_file,
        ligand=ligand_file,
        output_dir=output_dir,
        autobox_ligand=ligand_file,
        exhaustiveness=1, # Fast test
        n_poses=1,
        engine="smina"
    )
    
    assert "affinity" in result
    assert (output_dir / "docking_results" / "docked.pdbqt").exists()

@pytest.mark.skipif(not shutil.which("gnina"), reason="Gnina not installed")
def test_gnina_docking_pipeline(tmp_path):
    """Test full docking pipeline with Gnina using real data."""
    # Find input files
    receptor_file = list(RECEPTOR_DIR.glob("*.cif"))[0]
    ligand_file = list(LIGAND_DIR.glob("*.sdf"))[0]
    
    # Use persistent output directory
    output_dir = OUTPUT_DIR / "gnina"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run docking
    result = run_docking(
        receptor=receptor_file,
        ligand=ligand_file,
        output_dir=output_dir,
        autobox_ligand=ligand_file,
        exhaustiveness=1, # Fast test
        n_poses=1,
        engine="gnina"
    )
    
    assert "affinity" in result
    # Check for CNN scores if possible, though mock might not return them if binary output is not parsed correctly or different
    # But real binary should output them.
    # Note: Gnina binary output might vary, but our parser handles it.
    assert (output_dir / "docking_results" / "docked.pdbqt").exists()
