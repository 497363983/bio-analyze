from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_docking.prep import prepare_ligand


def prepare_ligand_cmd(
    input_file: Path = Argument(
        ..., help=_("Input ligand file (SDF, SMILES, PDB).")
    ),
    output_file: Path = Option(..., "-o", "--output", help=_("Output PDBQT file.")),
    add_hydrogens: bool = Option(True, help=_("Add hydrogens.")),
) -> None:
    """
    Prepare ligand for docking (SDF/SMILES -> PDBQT).

    Args:
        input_file (Path):
            Path to input ligand file (SDF, MOL2, PDB, SMI).
        output_file (Path):
            Path to output PDBQT file.
        add_hydrogens (bool, optional):
            Whether to automatically add hydrogens and generate 3D conformation. Defaults to True.
    """
    prepare_ligand(input_file, output_file, add_hydrogens=add_hydrogens)
    echo(f"Ligand prepared: {output_file}")
