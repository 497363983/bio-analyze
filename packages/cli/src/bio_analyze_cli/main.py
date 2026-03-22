from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from bio_analyze_core import load_settings, setup_logging
from bio_analyze_core.cli_i18n import detect_language, localize_app

from .commands.create import create_command
from .plugins import attach_plugins, load_plugins


def create_app() -> typer.Typer:
    """
    zh: 创建并配置 Typer 应用实例。
    en: Create and configure Typer app instance.

    Returns:
        typer.Typer:
            zh: 配置好的 Typer 应用实例。
            en: Configured Typer app instance.
    """
    app = typer.Typer(no_args_is_help=True)

    @app.callback()
    def _root(
        config: Optional[Path] = typer.Option(  # noqa: UP045 - Python 3.9 compatibility for runtime type-hint evaluation in Typer
            None,
            "--config",
            envvar="BIO_ANALYSE_CONFIG",
            help="zh: 配置文件路径 (.toml)。\nen: Path to config TOML.",
        ),
    ) -> None:
        """
        zh: Bio Analyze 命令行工具入口。
        en: Bio Analyze Command Line Interface.

        Args:
            config (Path | None, optional):
                zh: 配置文件路径。
                en: Path to configuration file.
        """
        # 加载配置和设置日志
        settings = load_settings(config_path=config)
        setup_logging(settings.log_level)

    @app.command("plugins")
    def _plugins() -> None:
        """
        zh: 列出所有已加载的插件。
        en: List all loaded plugins.
        """
        # 列出所有已加载的插件
        for p in load_plugins():
            typer.echo(p.name)

    app.command("create")(create_command)

    # 挂载插件到主命令
    attach_plugins(app)
    return app


app = create_app()


def main() -> None:
    lang = detect_language()
    localize_app(app, lang)
    app()


if __name__ == "__main__":
    main()
