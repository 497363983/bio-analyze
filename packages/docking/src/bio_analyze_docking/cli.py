from __future__ import annotations

import typer

from bio_analyze_core.cli_i18n import detect_language, localize_app

from .commands.prepare_ligand import prepare_ligand_cmd
from .commands.prepare_receptor import prepare_receptor_cmd
from .commands.run_gnina import run_gnina_cmd
from .commands.run_haddock import run_haddock_cmd
from .commands.run_smina import run_smina_cmd
from .commands.run_vina import run_vina_cmd


def get_app() -> typer.Typer:
    """
    zh: 获取 Docking 模块的 Typer 应用实例。
    en: Get the Typer app instance for the Docking module.

    Returns:
        typer.Typer:
            zh: 配置好的 Typer 应用。
            en: Configured Typer app.
    """
    app = typer.Typer(help="zh: 分子对接工具。\nen: Molecular docking tools.")

    app.command("prepare-receptor")(prepare_receptor_cmd)
    app.command("prepare-ligand")(prepare_ligand_cmd)

    run_app = typer.Typer(help="zh: 运行分子对接流程。\nen: Run molecular docking pipeline.")
    app.add_typer(run_app, name="run")

    run_app.command("vina")(run_vina_cmd)
    run_app.command("smina")(run_smina_cmd)
    run_app.command("gnina")(run_gnina_cmd)
    run_app.command("haddock")(run_haddock_cmd)

    localize_app(app, detect_language())
    return app
