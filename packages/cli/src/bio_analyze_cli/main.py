from __future__ import annotations

from pathlib import Path

from bio_analyze_core import load_settings, setup_logging
from bio_analyze_core.cli.app import BioAnalyzeTyper, echo, get_app
from bio_analyze_core.cli_i18n import localize_app
from bio_analyze_core.i18n import _

from .commands.create import create_command
from .plugins import attach_plugins, load_plugins


def create_app(*, load_plugin_apps: bool = False) -> BioAnalyzeTyper:
    app = get_app(
        name="bioanalyze",
        no_args_is_help=True,
        locale_path=Path(__file__).resolve().parents[2] / "locale",
        help=_("Path to config TOML."),
    )

    @app.callback()
    def _root() -> None:
        settings = load_settings()
        setup_logging(settings.log_level)

    @app.command("plugins")
    def _plugins() -> None:
        """List all loaded plugins."""
        for p in load_plugins():
            echo(p.name)

    app.command("create")(create_command)
    if load_plugin_apps:
        attach_plugins(app)
    return app


app = create_app()


def main() -> None:
    settings = load_settings()
    runtime_app = create_app(load_plugin_apps=True)
    localize_app(runtime_app, settings=settings)
    runtime_app()


if __name__ == "__main__":
    main()
