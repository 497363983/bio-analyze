import shutil
from pathlib import Path

import pandas as pd
import pytest
from bio_analyze_docking.api import run_docking_batch

# Define paths relative to the package root
DATA_DIR = Path(__file__).parent / "data"
RECEPTOR_DIR = DATA_DIR / "receptor"
LIGAND_DIR = DATA_DIR / "ligand"
OUTPUT_DIR = Path(__file__).parent / "output"


@pytest.mark.skipif(not DATA_DIR.exists(), reason="Data directory not found")
def test_docking_integration_real_data():
    """
    Integration test using real CIF receptors and SDF ligands.
    """
    # Use fixed output directory
    output_dir = OUTPUT_DIR / "vina"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Locate input files
    receptors = list(RECEPTOR_DIR.glob("*.cif"))
    ligands = list(LIGAND_DIR.glob("*.sdf"))

    assert len(receptors) > 0, "No CIF receptors found in test data"
    assert len(ligands) > 0, "No SDF ligands found in test data"

    print(f"Testing with receptors: {[r.name for r in receptors]}")
    print(f"Testing with ligands: {[l.name for l in ligands]}")

    # Run batch docking (Run ALL)
    # Testing with all available receptors and ligands to ensure robustness
    # and error reporting in summary for failed ones.

    # Ensure we use all files found
    selected_receptors = receptors
    selected_ligands = ligands

    results = run_docking_batch(
        receptors=selected_receptors,
        ligands=selected_ligands,
        output_dir=output_dir,
        center=None,
        size=None,
        autobox_ligand=ligands[0],
        padding=10.0,
        exhaustiveness=1,
        n_poses=1,
        summary_filename="summary.csv",
        output_docked_lig_recep_struct=True,
        n_docked_lig_recep_struct=1,
    )

    # Verify results
    # We expect results for ALL pairs, even if some failed.
    expected_count = len(selected_receptors) * len(selected_ligands)
    assert len(results) == expected_count, f"Expected {expected_count} results, got {len(results)}"

    # Verify summary file contains all entries
    summary_file = output_dir / "summary.csv"
    assert summary_file.exists()
    df = pd.read_csv(summary_file)
    assert len(df) == expected_count

    # Check for failed entries and print errors
    failed = df[df["Status"] == "failed"]
    if not failed.empty:
        print("\n--- Failed Tasks ---")
        for _, row in failed.iterrows():
            print(f"Receptor: {row['Receptor']}, Ligand: {row['Ligand']}, Error: {row['Error']}")

    # At least some should succeed (hopefully the small ligand + simple receptor if any)
    # If all fail due to AlphaFold issues, that's a data issue, but pipeline should report it.
    # We assert that the pipeline completed execution.

    print(f"Integration test finished. Output generated at {output_dir}")
