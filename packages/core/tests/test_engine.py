"""Unit tests for the shared core engine runtime."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from bio_analyze_core.engine import (
    BaseEngine,
    EngineConfig,
    EngineContext,
    EngineLifecycleState,
    EngineManager,
    EngineRegistry,
    EngineSpec,
    register_engine,
)


@dataclass
class DummyResult:
    """Simple result object used to verify metadata attachment."""
    value: str
    metadata: dict = field(default_factory=dict)


@register_engine(
    EngineSpec(
        domain="test",
        name="dummy",
        description="Dummy engine for core engine tests.",
    )
)
class DummyEngine(BaseEngine):
    """Minimal engine used to exercise the happy-path lifecycle."""

    def __init__(self, *args, payload: str = "ok", **kwargs):
        super().__init__(*args, **kwargs)
        self.payload = payload

    def execute(self) -> DummyResult:
        self.record_metadata("payload", self.payload)
        return DummyResult(self.payload)


@register_engine(
    EngineSpec(
        domain="test",
        name="requires-bin",
        required_binaries=("definitely-missing-binary",),
    )
)
class MissingDependencyEngine(BaseEngine):
    """Engine that declares a missing binary to test failure reporting."""

    def execute(self) -> DummyResult:
        return DummyResult("never")


@pytest.fixture(autouse=True)
def cleanup_test_domain():
    """Ensure the temporary test domain is registered and cleaned between tests."""
    EngineRegistry.register(DummyEngine.get_spec(), DummyEngine)
    EngineRegistry.register(MissingDependencyEngine.get_spec(), MissingDependencyEngine)
    yield
    EngineRegistry.clear(domain="test")


def test_engine_registry_register_get_list_unregister():
    """Registry APIs should register, list, and unregister engines correctly."""
    spec = EngineRegistry.get_spec("test", "dummy")

    assert spec.domain == "test"
    assert spec.name == "dummy"
    assert EngineRegistry.get("test", "dummy") is DummyEngine
    assert [item.name for item in EngineRegistry.list(domain="test")] == ["dummy", "requires-bin"]

    EngineRegistry.unregister("test", "dummy")

    with pytest.raises(ValueError, match="Unsupported engine 'test:dummy'"):
        EngineRegistry.get("test", "dummy")


def test_base_engine_run_tracks_lifecycle_and_attaches_metadata(tmp_path):
    """Successful runs should populate normalized lifecycle metrics."""
    engine = DummyEngine(
        context=EngineContext(output_dir=tmp_path, threads=2),
        config=EngineConfig(template="fast"),
        payload="done",
    )

    result = engine.run()

    assert result.value == "done"
    assert result.metadata["engine_domain"] == "test"
    assert result.metadata["engine_name"] == "dummy"
    assert result.metadata["engine_metrics"]["state"] == EngineLifecycleState.STOPPED.value
    assert result.metadata["engine_metrics"]["metadata"]["payload"] == "done"


def test_base_engine_run_records_failure_metrics():
    """Failed runs should record failure state and the last error message."""
    engine = MissingDependencyEngine()

    with pytest.raises(RuntimeError, match="Missing required external tools"):
        engine.run()

    metrics = engine.get_metrics_snapshot()
    assert metrics.state == EngineLifecycleState.FAILED
    assert metrics.failure_count == 1
    assert "definitely-missing-binary" in str(metrics.last_error)


def test_engine_manager_creates_and_switches_engines():
    """EngineManager should create engines and switch future selections."""
    manager = EngineManager(domain="test", engine_name="dummy", config={"template": "default"})

    engine = manager.create_engine(payload="first")
    first_result = engine.run()
    assert first_result.value == "first"

    @register_engine(EngineSpec(domain="test", name="alternate"))
    class AlternateDummyEngine(DummyEngine):
        """Secondary engine used to verify runtime switching."""

    assert AlternateDummyEngine is not None
    manager.switch_engine("alternate", config={"template": "alt"})

    second_engine = manager.create_engine(payload="second")
    second_result = second_engine.run()

    assert second_result.value == "second"
    assert manager.get_current_spec().name == "alternate"
    metrics = manager.get_metrics()
    assert "test:dummy" in metrics
    assert "test:alternate" in metrics
