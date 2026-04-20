from bio_analyze_core.i18n import _
from pathlib import Path

from bio_analyze_core.cli.app import BioAnalyzeTyper, Option, get_app as build_app
from bio_analyze_core.cli_i18n import localize_app

from bio_analyze_core.logging import setup_logging
from .commands.align import align_cmd
from .commands.tree import tree_cmd

def get_app() -> BioAnalyzeTyper:
    app = build_app(
        name="msa",
        help=_("Multiple Sequence Alignment and Phylogenetic Tree tools"),
        no_args_is_help=True,
        locale_path=Path(__file__).resolve().parents[2] / "locale",
    )

    # Common callback to setup logging
    @app.callback()
    def callback(
        verbose: bool = Option(False, "--verbose", help=_("Enable verbose logging"), is_flag=True),
    ):
        setup_logging(level="DEBUG" if verbose else "INFO")

    app.command("align")(align_cmd)
    app.command("tree")(tree_cmd)

    localize_app(app)
    return app

if __name__ == "__main__":
    get_app()()
