from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Argument, Option, echo
from bio_analyze_core.i18n import _
from bio_analyze_docking.prep import prepare_receptor


def prepare_receptor_cmd(
    input_file: Path = Argument(..., help=_("Input receptor file (PDB).")),
    output_file: Path = Option(..., "-o", "--output", help=_("Output PDBQT file.")),
    add_hydrogens: bool = Option(True, help=_("Add hydrogens.")),
    charge_model: str = Option(
        "gasteiger",
        "--charge-model",
        help=_("Charge model (gasteiger, zero, etc.)."),
    ),
) -> None:
    """
    Prepare receptor for docking (PDB -> PDBQT).

    Args:
        input_file (Path):
            Path to input receptor file (PDB/CIF).
        output_file (Path):
            Path to output PDBQT file.
        add_hydrogens (bool, optional):
            Whether to automatically add polar hydrogens. Defaults to True.
        charge_model (str, optional):
            Charge calculation model (gasteiger, kollman, zero). Defaults to 'gasteiger'.
    """
    prepare_receptor(input_file, output_file, add_hydrogens=add_hydrogens, charge_model=charge_model)
    echo(f"Receptor prepared: {output_file}")
