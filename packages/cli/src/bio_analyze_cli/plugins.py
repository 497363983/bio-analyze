from __future__ import annotations

import sys
from collections.abc import Iterable
from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from typing import Any

from bio_analyze_core.cli.app import BioAnalyzeTyper

ENTRYPOINT_GROUP = "bio_analyze.cli"

@dataclass(frozen=True, **({"slots": True} if sys.version_info >= (3, 10) else {}))
class CliPlugin:
    """
    CLI Plugin data class.

    Attributes:
        name (str):
            Plugin name.
        app (BioAnalyzeTyper):
            Typer application instance.
    """

    name: str
    app: BioAnalyzeTyper

def _iter_entry_points() -> Iterable[EntryPoint]:
    """
    Iterate over all registered entry points.

    Returns:
        Iterable[EntryPoint]:
            Iterable of EntryPoints.
    """
    eps = entry_points()
    if hasattr(eps, "select"):
        return eps.select(group=ENTRYPOINT_GROUP)
    return eps.get(ENTRYPOINT_GROUP, [])

def _load_typer(obj: Any) -> BioAnalyzeTyper:
    """
    Load Typer instance from object.

    Args:
        obj (Any):
            Target object (Typer instance or callable returning Typer instance).

    Returns:
        BioAnalyzeTyper:
            Typer application instance.

    Raises:
        TypeError:
            If object is not a Typer instance or a callable returning a Typer instance.
    """
    if isinstance(obj, BioAnalyzeTyper):
        return obj
    if callable(obj):
        app = obj()
        if isinstance(app, BioAnalyzeTyper):
            return app
    raise TypeError("CLI plugin must be a BioAnalyzeTyper app or a callable returning a BioAnalyzeTyper app.")

def load_plugins() -> list[CliPlugin]:
    """
    Load all available plugins.

    Returns:
        list[CliPlugin]:
            List of loaded plugins, sorted by name.
    """
    plugins: list[CliPlugin] = []
    for ep in _iter_entry_points():
        app = _load_typer(ep.load())
        plugins.append(CliPlugin(name=ep.name, app=app))
    return sorted(plugins, key=lambda p: p.name)

def attach_plugins(root: BioAnalyzeTyper) -> None:
    """
    Attach plugins to root command.

    Args:
        root (BioAnalyzeTyper):
            Root Typer application instance.
    """
    for plugin in load_plugins():
        root.add_typer(plugin.app, name=plugin.name)
