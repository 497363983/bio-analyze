from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from typing import Callable, Iterable, Any

import typer


ENTRYPOINT_GROUP = "bio_analyze.cli"


@dataclass(frozen=True, slots=True)
class CliPlugin:
    """CLI 插件数据类。"""
    name: str
    app: typer.Typer


def _iter_entry_points() -> Iterable[EntryPoint]:
    eps = entry_points()
    if hasattr(eps, "select"):
        return eps.select(group=ENTRYPOINT_GROUP)
    return eps.get(ENTRYPOINT_GROUP, [])


def _load_typer(obj: Any) -> typer.Typer:
    """从对象加载 Typer 实例。"""
    if isinstance(obj, typer.Typer):
        return obj
    if callable(obj):
        app = obj()
        if isinstance(app, typer.Typer):
            return app
    raise TypeError("CLI plugin must be a Typer app or a callable returning a Typer app.")


def load_plugins() -> list[CliPlugin]:
    """加载所有可用插件。"""
    plugins: list[CliPlugin] = []
    for ep in _iter_entry_points():
        app = _load_typer(ep.load())
        plugins.append(CliPlugin(name=ep.name, app=app))
    return sorted(plugins, key=lambda p: p.name)


def attach_plugins(root: typer.Typer) -> None:
    """将插件挂载到根命令。"""
    for plugin in load_plugins():
        root.add_typer(plugin.app, name=plugin.name)

