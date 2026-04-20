from __future__ import annotations
from pathlib import Path

from bio_analyze_core.cli.app import BioAnalyzeTyper, get_app as build_app
from bio_analyze_core.cli_i18n import localize_app
from bio_analyze_core.i18n import _

from .commands.align import run_align
from .commands.de import run_de
from .commands.download import download_sra
from .commands.enrich import run_enrich
from .commands.genome import prepare_genome
from .commands.gsea import run_gsea
from .commands.qc import run_qc
from .commands.quant import run_quant
from .commands.run import run_analysis


def get_app() -> BioAnalyzeTyper:
    app = build_app(
        help=_("Transcriptomics analysis workflow."),
        locale_path=Path(__file__).resolve().parents[3] / "locale",
    )

    app.command("run")(run_analysis)
    app.command("download")(download_sra)
    app.command("genome")(prepare_genome)
    app.command("qc")(run_qc)
    app.command("align")(run_align)
    app.command("quant")(run_quant)
    app.command("de")(run_de)
    app.command("enrich")(run_enrich)
    app.command("gsea")(run_gsea)

    localize_app(app)
    return app
