from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_core import load_settings, setup_logging
from .plugins import attach_plugins, load_plugins


def create_app() -> typer.Typer:
    app = typer.Typer(no_args_is_help=True)

    @app.callback()
    def _root(
        config: Path | None = typer.Option(
            None,
            "--config",
            envvar="BIO_ANALYSE_CONFIG",
            help="Path to config TOML.",
        ),
    ) -> None:
        # 加载配置和设置日志
        settings = load_settings(config_path=config)
        setup_logging(settings.log_level)

    @app.command("plugins")
    def _plugins() -> None:
        # 列出所有已加载的插件
        for p in load_plugins():
            typer.echo(p.name)

    # 挂载插件到主命令
    attach_plugins(app)
    return app


app = create_app()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
