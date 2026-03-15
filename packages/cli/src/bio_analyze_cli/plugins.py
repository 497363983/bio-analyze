from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from typing import Any

import typer

ENTRYPOINT_GROUP = "bio_analyze.cli"


@dataclass(frozen=True, slots=True)
class CliPlugin:
    """
    zh: CLI 插件数据类。
    en: CLI Plugin data class.

    Attributes:
        name (str):
            zh: 插件名称。
            en: Plugin name.
        app (typer.Typer):
            zh: Typer 应用实例。
            en: Typer application instance.
    """

    name: str
    app: typer.Typer


def _iter_entry_points() -> Iterable[EntryPoint]:
    """
    zh: 迭代所有注册的 entry points。
    en: Iterate over all registered entry points.

    Returns:
        Iterable[EntryPoint]:
            zh: EntryPoint 迭代器。
            en: Iterable of EntryPoints.
    """
    eps = entry_points()
    if hasattr(eps, "select"):
        return eps.select(group=ENTRYPOINT_GROUP)
    return eps.get(ENTRYPOINT_GROUP, [])


def _load_typer(obj: Any) -> typer.Typer:
    """
    zh: 从对象加载 Typer 实例。
    en: Load Typer instance from object.

    Args:
        obj (Any):
            zh: 目标对象（Typer 实例或返回 Typer 实例的可调用对象）。
            en: Target object (Typer instance or callable returning Typer instance).

    Returns:
        typer.Typer:
            zh: Typer 应用实例。
            en: Typer application instance.

    Raises:
        TypeError:
            zh: 如果对象不是 Typer 实例或返回 Typer 实例的可调用对象。
            en: If object is not a Typer instance or a callable returning a Typer instance.
    """
    if isinstance(obj, typer.Typer):
        return obj
    if callable(obj):
        app = obj()
        if isinstance(app, typer.Typer):
            return app
    raise TypeError("CLI plugin must be a Typer app or a callable returning a Typer app.")


def load_plugins() -> list[CliPlugin]:
    """
    zh: 加载所有可用插件。
    en: Load all available plugins.

    Returns:
        list[CliPlugin]:
            zh: 已加载的插件列表，按名称排序。
            en: List of loaded plugins, sorted by name.
    """
    plugins: list[CliPlugin] = []
    for ep in _iter_entry_points():
        app = _load_typer(ep.load())
        plugins.append(CliPlugin(name=ep.name, app=app))
    return sorted(plugins, key=lambda p: p.name)


def attach_plugins(root: typer.Typer) -> None:
    """
    zh: 将插件挂载到根命令。
    en: Attach plugins to root command.

    Args:
        root (typer.Typer):
            zh: 根 Typer 应用实例。
            en: Root Typer application instance.
    """
    for plugin in load_plugins():
        root.add_typer(plugin.app, name=plugin.name)
