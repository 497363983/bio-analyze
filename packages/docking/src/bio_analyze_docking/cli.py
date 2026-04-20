from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import BioAnalyzeTyper
from bio_analyze_core.cli.app import get_app as build_app
from bio_analyze_core.cli_i18n import localize_app
from bio_analyze_core.i18n import _

from .commands.prepare_ligand import prepare_ligand_cmd
from .commands.prepare_receptor import prepare_receptor_cmd
from .commands.run_gnina import run_gnina_cmd
from .commands.run_haddock import run_haddock_cmd
from .commands.run_smina import run_smina_cmd
from .commands.run_vina import run_vina_cmd


def get_app() -> BioAnalyzeTyper:
    """Get the CLI app for the docking module."""
    app = build_app(
        help=_("Molecular docking tools."),
        locale_path=Path(__file__).resolve().parents[2] / "locale",
    )

    app.command("prepare-receptor")(prepare_receptor_cmd)
    app.command("prepare-ligand")(prepare_ligand_cmd)

    run_app = build_app(
        help=_("Run molecular docking pipeline."),
        locale_path=Path(__file__).resolve().parents[2] / "locale",
    )
    app.add_typer(run_app, name="run")

    run_app.command("vina")(run_vina_cmd)
    run_app.command("smina")(run_smina_cmd)
    run_app.command("gnina")(run_gnina_cmd)
    run_app.command("haddock")(run_haddock_cmd)

    localize_app(app)
    return app
