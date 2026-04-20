from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Option
from bio_analyze_core.i18n import _
from bio_analyze_docking.commands.utils import execute_docking_cli


def run_smina_cmd(
    config_file: Path | None = Option(
        None, "--config", "-c", help=_("Config file path.")
    ),
    receptor: Path | None = Option(
        None, "-r", "--receptor", help=_("Receptor file/dir.")
    ),
    ligand: Path | None = Option(None, "-l", "--ligand", help=_("Ligand file/dir.")),
    output_dir: Path | None = Option(None, "-o", "--output", help=_("Output dir.")),
    center_x: float | None = Option(None, help=_("Box center X.")),
    center_y: float | None = Option(None, help=_("Box center Y.")),
    center_z: float | None = Option(None, help=_("Box center Z.")),
    size_x: float | None = Option(None, help=_("Box size X.")),
    size_y: float | None = Option(None, help=_("Box size Y.")),
    size_z: float | None = Option(None, help=_("Box size Z.")),
    autobox_ligand: Path | None = Option(None, help=_("Reference ligand.")),
    padding: float | None = Option(None, help=_("Autobox padding.")),
    exhaustiveness: int | None = Option(None, help=_("Exhaustiveness.")),
    n_poses: int | None = Option(None, help=_("Number of poses.")),
    charge_model: str | None = Option(None, "--charge-model", help=_("Charge model.")),
) -> None:
    """
    Run molecular docking using Smina engine.
    """
    execute_docking_cli(
        "smina",
        config_file,
        receptor,
        ligand,
        output_dir,
        center_x,
        center_y,
        center_z,
        size_x,
        size_y,
        size_z,
        autobox_ligand,
        padding,
        exhaustiveness,
        n_poses,
        charge_model,
    )
