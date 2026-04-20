from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import Option
from bio_analyze_core.i18n import _
from bio_analyze_docking.commands.utils import execute_docking_cli


def run_haddock_cmd(
    config_file: Path | None = Option(
        None, "--config", "-c", help=_("Config file path.")
    ),
    receptor: Path | None = Option(
        None, "-r", "--receptor", help=_("Receptor file/dir.")
    ),
    ligand: Path | None = Option(None, "-l", "--ligand", help=_("Ligand file/dir.")),
    output_dir: Path | None = Option(None, "-o", "--output", help=_("Output dir.")),
    n_poses: int | None = Option(None, help=_("Number of poses to sample.")),
    charge_model: str | None = Option(None, "--charge-model", help=_("Charge model.")),
    haddock_config: Path | None = Option(
        None,
        "--haddock-config",
        help=_("Custom HADDOCK3 configuration file path."),
    ),
) -> None:
    """
    Run molecular docking using HADDOCK engine.
    """
    # Haddock 不使用 Box 参数，也不使用 exhaustiveness
    execute_docking_cli(
        "haddock",
        config_file,
        receptor,
        ligand,
        output_dir,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        100,
        n_poses,
        charge_model,
        haddock_config,
    )
