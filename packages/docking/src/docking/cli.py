from __future__ import annotations

from pathlib import Path

import typer

from .api import example_dock


def get_app() -> typer.Typer:
    app = typer.Typer(help="Molecular docking tools.")

    @app.command("example")
    def _example(receptor_pdb: Path, ligand_sdf: Path) -> None:
        result = example_dock(receptor_pdb, ligand_sdf)
        typer.echo(result)

    return app

