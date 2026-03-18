from pathlib import Path
from unittest.mock import patch

import pytest
from bio_analyze_docking.prep import get_box_from_ligand, prepare_ligand, prepare_receptor

# Define paths relative to the test file
DATA_DIR = Path(__file__).parent / "data"
RECEPTOR_DIR = DATA_DIR / "receptor"
LIGAND_DIR = DATA_DIR / "ligand"


@pytest.fixture
def output_dir(tmp_path):
    """Temporary directory for test outputs."""
    out = tmp_path / "prep_output"
    out.mkdir(exist_ok=True)
    return out


@pytest.mark.skipif(not DATA_DIR.exists(), reason="Data directory not found")
def test_prepare_receptor_cif(output_dir):
    """Test preparing a receptor from CIF format (Real integration test)."""
    # Use one of the real CIF files
    cif_files = list(RECEPTOR_DIR.glob("*.cif"))
    assert len(cif_files) > 0, "No CIF files found for testing"

    # Use the first one (e.g. fold_tlr_7...)
    input_file_src = cif_files[0]

    # Copy to temp dir with shorter name to avoid path length issues on Windows
    input_file = output_dir / "test_rec.cif"
    import shutil

    shutil.copy(input_file_src, input_file)

    output_file = output_dir / "test_rec.pdbqt"

    # Run preparation
    result_path = prepare_receptor(
        input_file=input_file,
        output_file=output_file,
        add_hydrogens=True,
        ph=7.4,
        charge_model="gasteiger",  # Default
    )

    assert result_path.exists()
    assert result_path.suffix == ".pdbqt"
    assert result_path.stat().st_size > 0

    # Check content for PDBQT specific tags
    content = result_path.read_text()
    assert "ATOM" in content
    # Should NOT contain ROOT/ENDROOT for rigid receptor
    assert "ROOT" not in content
    assert "ENDROOT" not in content
    assert "TORSDOF" not in content


@pytest.mark.skipif(not DATA_DIR.exists(), reason="Data directory not found")
def test_prepare_receptor_charge_model(output_dir):
    """Test receptor preparation with different charge models."""
    # Use a simpler/smaller CIF if possible, or same one
    cif_files = list(RECEPTOR_DIR.glob("*.cif"))

    input_file_src = cif_files[0]
    input_file = output_dir / "test_rec_charge.cif"
    import shutil

    shutil.copy(input_file_src, input_file)

    output_file = output_dir / "test_rec_charge.pdbqt"

    # Run with 'zero' charge model (faster/safer)
    result_path = prepare_receptor(
        input_file=input_file, output_file=output_file, add_hydrogens=True, charge_model="zero"
    )

    assert result_path.exists()
    content = result_path.read_text()
    assert "ATOM" in content

    # Verify charges are zero (last column before element symbol usually)
    # PDBQT format: ... x y z occupancy tempFactor charge element
    # Check a few lines
    lines = [li for li in content.splitlines() if li.startswith("ATOM")]
    if lines:
        # PDBQT charge is at column 70-76 (1-based index) -> 69:76
        # Or just parse last float
        charge_str = lines[0][69:76].strip()
        try:
            charge = float(charge_str)
            assert abs(charge) < 0.001, f"Expected zero charge, got {charge}"
        except ValueError:
            pass  # Parsing failed


@pytest.mark.skipif(not DATA_DIR.exists(), reason="Data directory not found")
def test_prepare_ligand_sdf(output_dir):
    """Test preparing a ligand from SDF format."""
    sdf_files = list(LIGAND_DIR.glob("*.sdf"))
    assert len(sdf_files) > 0, "No SDF files found for testing"

    input_file = sdf_files[0]
    output_file = output_dir / f"{input_file.stem}.pdbqt"

    result_path = prepare_ligand(input_file, output_file)

    assert result_path.exists()
    assert result_path.stat().st_size > 0

    content = result_path.read_text()
    assert "ROOT" in content  # Flexible ligand should have ROOT
    assert "TORSDOF" in content


def test_prepare_ligand_smiles(output_dir):
    """Test preparing a ligand from SMILES file."""
    # Create a dummy smiles file
    smiles_file = output_dir / "test.smi"
    smiles_file.write_text("CCO")  # Ethanol
    output_file = output_dir / "ethanol.pdbqt"

    result_path = prepare_ligand(smiles_file, output_file)

    assert result_path.exists()
    content = result_path.read_text()
    assert "ROOT" in content
    assert "ATOM" in content


@pytest.mark.skipif(not DATA_DIR.exists(), reason="Data directory not found")
def test_prepare_ligand_cif(output_dir):
    """Test preparing a ligand from CIF format (with mocked conversion)."""
    input_cif = output_dir / "test_lig.cif"
    input_cif.touch()  # Create dummy CIF
    
    output_file = output_dir / "test_lig.pdbqt"
    
    # Valid PDB content for Methane (CH4)
    valid_pdb_content = """CRYST1   10.000   10.000   10.000  90.00  90.00  90.00 P 1           1
ATOM      1  C   LIG     1       0.000   0.000   0.000  1.00  0.00           C  
ATOM      2  H   LIG     1       0.629   0.629   0.629  1.00  0.00           H  
ATOM      3  H   LIG     1      -0.629  -0.629   0.629  1.00  0.00           H  
ATOM      4  H   LIG     1      -0.629   0.629  -0.629  1.00  0.00           H  
ATOM      5  H   LIG     1       0.629  -0.629  -0.629  1.00  0.00           H  
TER       6      LIG     1
END
"""

    def mock_convert(input_file, output_file=None):
        if output_file is None:
             output_file = input_file.parent / f"{input_file.stem}_converted.pdb"
        output_file.write_text(valid_pdb_content)
        return output_file

    with patch("bio_analyze_docking.prep.convert_cif_to_pdb", side_effect=mock_convert) as mock_conv:
        result_path = prepare_ligand(input_cif, output_file)
        
        assert mock_conv.called
        assert result_path.exists()
        assert result_path.stat().st_size > 0
        content = result_path.read_text()
        assert "ATOM" in content


@pytest.mark.skipif(not DATA_DIR.exists(), reason="Data directory not found")
def test_get_box_from_ligand():
    """Test bounding box calculation."""
    sdf_files = list(LIGAND_DIR.glob("*.sdf"))
    if not sdf_files:
        pytest.skip("No SDF files for box test")

    input_file = sdf_files[0]
    center, size = get_box_from_ligand(input_file, padding=4.0)

    assert len(center) == 3
    assert len(size) == 3
    assert all(isinstance(x, float) for x in center)
    assert all(x > 0 for x in size)
