from __future__ import annotations

import typer

from bio_analyze_core.cli_i18n import detect_language, localize_app

from .commands.align import run_align
from .commands.de import run_de
from .commands.download import download_sra
from .commands.enrich import run_enrich
from .commands.genome import prepare_genome
from .commands.gsea import run_gsea
from .commands.qc import run_qc
from .commands.quant import run_quant
from .commands.run import run_analysis


def get_app() -> typer.Typer:
    app = typer.Typer(help="zh: 转录组分析工作流。\nen: Transcriptomics analysis workflow.")

    app.command("run")(run_analysis)
    app.command("download")(download_sra)
    app.command("genome")(prepare_genome)
    app.command("qc")(run_qc)
    app.command("align")(run_align)
    app.command("quant")(run_quant)
    app.command("de")(run_de)
    app.command("enrich")(run_enrich)
    app.command("gsea")(run_gsea)

    localize_app(app, detect_language())
    return app
