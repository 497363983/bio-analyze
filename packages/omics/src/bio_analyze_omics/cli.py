from __future__ import annotations

from pathlib import Path

from bio_analyze_core.cli.app import BioAnalyzeTyper
from bio_analyze_core.cli.app import get_app as build_app
from bio_analyze_core.cli_i18n import localize_app
from bio_analyze_core.i18n import _

from .rna_seq.cli import get_app as get_rna_seq_app


def get_app() -> BioAnalyzeTyper:
    app = build_app(
        help=_("Collection of omics analysis workflows."),
        locale_path=Path(__file__).resolve().parents[2] / "locale",
    )
    app.add_typer(get_rna_seq_app(), name="rna_seq")
    localize_app(app)
    return app
