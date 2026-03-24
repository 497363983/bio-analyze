import typer

from bio_analyze_core.logging import setup_logging
from .commands.align import align_cmd
from .commands.tree import tree_cmd

def get_app() -> typer.Typer:
    app = typer.Typer(
        name="msa",
        help="zh: 多序列比对和系统发育树工具\nen: Multiple Sequence Alignment and Phylogenetic Tree tools",
        no_args_is_help=True,
    )

    # Common callback to setup logging
    @app.callback()
    def callback(
        verbose: bool = typer.Option(False, "--verbose", "-v", help="zh: 启用详细日志\nen: Enable verbose logging"),
    ):
        setup_logging(level="DEBUG" if verbose else "INFO")

    app.command("align")(align_cmd)
    app.command("tree")(tree_cmd)

    return app

if __name__ == "__main__":
    get_app()()
