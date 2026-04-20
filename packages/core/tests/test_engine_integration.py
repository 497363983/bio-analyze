"""Integration-oriented tests for engine discovery and entry-point refresh."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from bio_analyze_core.engine import (
    BaseEngine,
    EngineRegistry,
    EngineSpec,
)


class EntryPointEngine(BaseEngine):
    """Stub engine loaded through a mocked entry-point object."""
    SPEC = EngineSpec(domain="integration", name="entrypoint", description="Loaded via entry point.")

    def execute(self) -> dict:
        return {"status": "ok"}


def test_engine_registry_refreshes_entry_points(monkeypatch):
    """Refreshing entry points should register newly discovered engines."""
    EngineRegistry.clear(domain="integration")

    entry_point = MagicMock()
    entry_point.name = "integration:entrypoint"
    entry_point.load.return_value = EntryPointEngine
    monkeypatch.setattr(
        "bio_analyze_core.engine._iter_engine_entry_points",
        lambda: [entry_point],
    )

    specs = EngineRegistry.refresh_entry_points()

    assert any(spec.domain == "integration" and spec.name == "entrypoint" for spec in specs)
    assert EngineRegistry.get("integration", "entrypoint") is EntryPointEngine

    EngineRegistry.clear(domain="integration")


def test_engine_registry_rejects_invalid_entry_point_name(monkeypatch):
    """Invalid entry-point names should fail fast with a clear error."""
    bad_entry_point = MagicMock()
    bad_entry_point.name = "invalid-name"
    bad_entry_point.load.return_value = EntryPointEngine
    monkeypatch.setattr(
        "bio_analyze_core.engine._iter_engine_entry_points",
        lambda: [bad_entry_point],
    )

    try:
        with pytest.raises(ValueError, match="Invalid engine entry point name"):
            EngineRegistry.refresh_entry_points()
    finally:
        EngineRegistry.clear(domain="integration")
