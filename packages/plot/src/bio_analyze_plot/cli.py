from __future__ import annotations

import typer

from bio_analyze_core.cli_i18n import detect_language, localize_app

from .commands.bar import bar_cmd
from .commands.box import box_cmd
from .commands.chromosome import chromosome_cmd
from .commands.gsea import gsea_cmd
from .commands.heatmap import heatmap_cmd
from .commands.line import line_cmd
from .commands.pca import pca_cmd
from .commands.pie import pie_cmd
from .commands.scatter import scatter_cmd
from .commands.volcano import volcano_cmd
from .commands.msa import msa_cmd
from .commands.tree import tree_cmd


def get_app() -> typer.Typer:
    app = typer.Typer(help="zh: 绘图工具\nen: Publication-ready plotting tools.")

    app.command("volcano")(volcano_cmd)
    app.command("line")(line_cmd)
    app.command("bar")(bar_cmd)
    app.command("box")(box_cmd)
    app.command("heatmap")(heatmap_cmd)
    app.command("pca")(pca_cmd)
    app.command("scatter")(scatter_cmd)
    app.command("pie")(pie_cmd)
    app.command("gsea")(gsea_cmd)
    app.command("chromosome")(chromosome_cmd)
    app.command("msa")(msa_cmd)
    app.command("tree")(tree_cmd)

    localize_app(app, detect_language())
    return app
