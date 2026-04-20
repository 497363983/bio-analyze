"""Performance regression tests for the shared core engine runtime."""

from __future__ import annotations

import time

from bio_analyze_core.engine import BaseEngine, EngineManager, EngineRegistry, EngineSpec, register_engine


def _make_engine_class(index: int):
    @register_engine(EngineSpec(domain="perf", name=f"engine-{index}"))
    class PerfEngine(BaseEngine):
        """Synthetic engine class used for performance benchmarks."""

        def execute(self) -> dict:
            return {"index": index}

    return PerfEngine


def test_engine_registry_bulk_registration_and_listing_is_fast_enough():
    """Bulk registration and listing should stay within a small runtime budget."""
    EngineRegistry.clear(domain="perf")

    start = time.perf_counter()
    for index in range(100):
        _make_engine_class(index)
    register_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    specs = EngineRegistry.list(domain="perf")
    list_elapsed = time.perf_counter() - start

    assert len(specs) == 100
    assert register_elapsed < 1.0
    assert list_elapsed < 0.2

    EngineRegistry.clear(domain="perf")


def test_engine_manager_switching_has_reasonable_overhead():
    """Repeated switching and instantiation should not regress dramatically."""
    EngineRegistry.clear(domain="perf")
    for index in range(20):
        _make_engine_class(index)

    manager = EngineManager(domain="perf", engine_name="engine-0")
    start = time.perf_counter()
    for index in range(1, 20):
        manager.switch_engine(f"engine-{index}")
        engine = manager.create_engine()
        result = engine.run()
        assert result["index"] == index
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0

    EngineRegistry.clear(domain="perf")
