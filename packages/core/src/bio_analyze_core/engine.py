"""Shared multi-engine runtime abstractions used across business modules."""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import Enum
from importlib.metadata import EntryPoint, entry_points
from pathlib import Path
from typing import Any, ClassVar, cast

from .logging import get_logger

ENGINE_ENTRYPOINT_GROUP = "bio_analyze.engine"
logger = get_logger(__name__)


class EngineLifecycleState(str, Enum):
    """Lifecycle states tracked by the shared engine runtime."""

    REGISTERED = "registered"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class EngineSpec:
    """Static metadata describing an engine implementation."""
    domain: str
    name: str
    version: str = "unknown"
    description: str = ""
    capabilities: tuple[str, ...] = ()
    required_binaries: tuple[str, ...] = ()

    @property
    def key(self) -> tuple[str, str]:
        """Return the registry key for the engine."""
        return (self.domain, self.name)

    @property
    def entrypoint_name(self) -> str:
        """Return the normalized entry-point name for package discovery."""
        return f"{self.domain}:{self.name}"


@dataclass
class EngineConfig:
    """Normalized runtime configuration passed to engine instances."""
    template: str = "default"
    phases: dict[str, list[str]] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    enable_monitoring: bool = True

    @classmethod
    def from_value(cls, value: Any) -> EngineConfig:
        """Build an ``EngineConfig`` from an existing instance or mapping."""
        if isinstance(value, cls):
            return value
        if not value:
            return cls()
        return cls(
            template=value.get("template", "default"),
            phases={
                key: [str(item) for item in items]
                for key, items in value.get("phases", {}).items()
            },
            params=dict(value.get("params", {})),
            options={
                key: val
                for key, val in value.items()
                if key not in {"template", "phases", "params", "options", "enable_monitoring"}
            }
            | dict(value.get("options", {})),
            enable_monitoring=bool(value.get("enable_monitoring", True)),
        )


@dataclass
class EngineMetricsSnapshot:
    """Execution metrics captured for a single engine instance."""
    state: EngineLifecycleState = EngineLifecycleState.REGISTERED
    registered_at: float = field(default_factory=time.time)
    initialized_at: float | None = None
    started_at: float | None = None
    finished_at: float | None = None
    execution_time: float | None = None
    switch_count: int = 0
    failure_count: int = 0
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the metrics snapshot into a plain dictionary."""
        return {
            "state": self.state.value,
            "registered_at": self.registered_at,
            "initialized_at": self.initialized_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "execution_time": self.execution_time,
            "switch_count": self.switch_count,
            "failure_count": self.failure_count,
            "last_error": self.last_error,
            "metadata": dict(self.metadata),
        }


@dataclass
class EngineContext:
    """Shared runtime context passed into engines."""
    output_dir: Path | None = None
    threads: int = 1
    logger: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)


class BaseEngine(ABC):
    """Base class that provides a common engine lifecycle wrapper."""
    SPEC = EngineSpec(domain="base", name="base")

    def __init__(
        self,
        context: EngineContext | None = None,
        config: EngineConfig | dict[str, Any] | None = None,
        **_: Any,
    ):
        self.context = context or EngineContext()
        self.config = EngineConfig.from_value(config)
        spec = self.get_spec()
        self.logger = self.context.logger or get_logger(
            f"{__name__}.{spec.domain}.{spec.name}"
        )
        self.metrics = EngineMetricsSnapshot()

    @classmethod
    def get_spec(cls) -> EngineSpec:
        """Return the static ``EngineSpec`` declared by the engine class."""
        return cls.SPEC

    def initialize(self) -> None:
        """Mark the engine as initialized before execution starts."""
        self.metrics.state = EngineLifecycleState.INITIALIZED
        self.metrics.initialized_at = time.time()

    def validate_inputs(self) -> None:
        """Validate inputs before execution; subclasses may override."""
        return None

    def shutdown(self) -> None:
        """Mark the engine as stopped after execution completes."""
        self.metrics.state = EngineLifecycleState.STOPPED
        if self.metrics.finished_at is None:
            self.metrics.finished_at = time.time()

    def check_dependencies(self) -> None:
        """Verify external binary dependencies declared by the engine spec."""
        spec = self.get_spec()
        missing = [
            tool for tool in spec.required_binaries if not self._which(tool)
        ]
        if missing:
            raise RuntimeError(
                f"Missing required external tools for engine '{spec.domain}:{spec.name}': "
                f"{', '.join(missing)}"
            )

    def record_metadata(self, key: str, value: Any) -> None:
        """Attach engine-specific metrics metadata to the current run."""
        self.metrics.metadata[key] = value

    def get_metrics_snapshot(self) -> EngineMetricsSnapshot:
        """Return the current metrics snapshot for the engine instance."""
        return self.metrics

    def run(self) -> Any:
        """Run the full engine lifecycle and return the execution result."""
        try:
            self.initialize()
            self.check_dependencies()
            self.validate_inputs()
            self.metrics.state = EngineLifecycleState.RUNNING
            self.metrics.started_at = time.time()
            result = self.execute()
        except Exception as exc:
            self.metrics.state = EngineLifecycleState.FAILED
            self.metrics.failure_count += 1
            self.metrics.last_error = str(exc)
            self.metrics.finished_at = time.time()
            started_at = self.metrics.started_at or self.metrics.initialized_at
            self.metrics.execution_time = (
                self.metrics.finished_at - started_at
                if started_at is not None
                else None
            )
            raise

        self.metrics.finished_at = time.time()
        self.metrics.execution_time = (
            self.metrics.finished_at - self.metrics.started_at
            if self.metrics.started_at is not None
            else None
        )
        self.shutdown()
        self._attach_result_metadata(result)
        return result

    def _attach_result_metadata(self, result: Any) -> None:
        """Populate normalized engine metadata on result objects when supported."""
        metadata = getattr(result, "metadata", None)
        if isinstance(metadata, dict):
            spec = self.get_spec()
            metadata.setdefault("engine_domain", spec.domain)
            metadata.setdefault("engine_name", spec.name)
            metadata.setdefault("engine_version", spec.version)
            metadata.setdefault("engine_capabilities", list(spec.capabilities))
            metadata.setdefault("engine_metrics", self.metrics.to_dict())

    @staticmethod
    def _which(name: str) -> str | None:
        """Locate an external executable in ``PATH``."""
        import shutil

        return shutil.which(name)

    @abstractmethod
    def execute(self) -> Any:
        """Execute the engine-specific workload."""
        raise NotImplementedError


def _iter_engine_entry_points() -> Iterable[EntryPoint]:
    """Yield engine entry points from installed packages."""
    eps: Any = entry_points()
    if hasattr(eps, "select"):
        return eps.select(group=ENGINE_ENTRYPOINT_GROUP)
    try:
        return cast(Iterable[EntryPoint], eps.get(ENGINE_ENTRYPOINT_GROUP, []))
    except AttributeError:
        pass
    return []


def _parse_entrypoint_name(name: str) -> tuple[str, str]:
    """Parse an entry-point name into ``(domain, engine_name)``."""
    if ":" not in name:
        raise ValueError(
            f"Invalid engine entry point name '{name}'. Expected '<domain>:<engine_name>'."
        )
    domain, engine_name = name.split(":", 1)
    if not domain or not engine_name:
        raise ValueError(
            f"Invalid engine entry point name '{name}'. Expected '<domain>:<engine_name>'."
        )
    return domain, engine_name


def _load_engine_class(obj: Any) -> type[BaseEngine]:
    """Resolve an entry point object into a ``BaseEngine`` subclass."""
    if isinstance(obj, type) and issubclass(obj, BaseEngine):
        return obj
    if callable(obj):
        loaded = obj()
        if isinstance(loaded, type) and issubclass(loaded, BaseEngine):
            return loaded
    raise TypeError(
        "Engine entry point must resolve to a BaseEngine subclass or a callable returning one."
    )


class EngineRegistry:
    """Global registry responsible for engine registration and discovery."""
    _registry: ClassVar[dict[tuple[str, str], type[BaseEngine]]] = {}
    _specs: ClassVar[dict[tuple[str, str], EngineSpec]] = {}
    _lock: ClassVar[threading.RLock] = threading.RLock()

    @classmethod
    def register(
        cls,
        spec: EngineSpec,
        engine_cls: type[BaseEngine],
    ) -> type[BaseEngine]:
        """Register an engine class under the provided spec."""
        key = spec.key
        with cls._lock:
            cls._registry[key] = engine_cls
            cls._specs[key] = spec
        return engine_cls

    @classmethod
    def unregister(cls, domain: str, name: str) -> None:
        """Remove an engine registration if it exists."""
        key = (domain, name)
        with cls._lock:
            cls._registry.pop(key, None)
            cls._specs.pop(key, None)

    @classmethod
    def get(cls, domain: str, name: str) -> type[BaseEngine]:
        """Return the registered engine class for a domain and name."""
        key = (domain, name)
        with cls._lock:
            try:
                return cls._registry[key]
            except KeyError as exc:
                available = ", ".join(
                    f"{spec.domain}:{spec.name}" for spec in cls.list(domain=domain)
                )
                raise ValueError(
                    f"Unsupported engine '{domain}:{name}'. Available engines: {available or 'none'}"
                ) from exc

    @classmethod
    def get_spec(cls, domain: str, name: str) -> EngineSpec:
        """Return the registered spec for a domain and name."""
        key = (domain, name)
        with cls._lock:
            try:
                return cls._specs[key]
            except KeyError as exc:
                raise ValueError(f"Unknown engine spec '{domain}:{name}'.") from exc

    @classmethod
    def list(cls, domain: str | None = None) -> list[EngineSpec]:
        """List all registered engine specs, optionally filtered by domain."""
        with cls._lock:
            specs = list(cls._specs.values())
        if domain is not None:
            specs = [spec for spec in specs if spec.domain == domain]
        return sorted(specs, key=lambda spec: (spec.domain, spec.name))

    @classmethod
    def refresh_entry_points(cls) -> list[EngineSpec]:
        """Refresh engine registrations from installed package entry points."""
        refreshed_specs: list[EngineSpec] = []
        for ep in _iter_engine_entry_points():
            domain, name = _parse_entrypoint_name(ep.name)
            engine_cls = _load_engine_class(ep.load())
            spec = getattr(engine_cls, "SPEC", None)
            if not isinstance(spec, EngineSpec):
                spec = EngineSpec(
                    domain=domain,
                    name=name,
                    description=(engine_cls.__doc__ or "").strip(),
                )
                engine_cls.SPEC = spec
            elif spec.domain != domain or spec.name != name:
                spec = EngineSpec(
                    domain=domain,
                    name=name,
                    version=spec.version,
                    description=spec.description,
                    capabilities=spec.capabilities,
                    required_binaries=spec.required_binaries,
                )
                engine_cls.SPEC = spec
            cls.register(spec, engine_cls)
            refreshed_specs.append(spec)
        return sorted(refreshed_specs, key=lambda spec: (spec.domain, spec.name))

    @classmethod
    def clear(cls, domain: str | None = None) -> None:
        """Clear the registry globally or for a single domain."""
        with cls._lock:
            if domain is None:
                cls._registry.clear()
                cls._specs.clear()
                return
            for key in list(cls._registry):
                if key[0] == domain:
                    cls._registry.pop(key, None)
                    cls._specs.pop(key, None)


def register_engine(spec: EngineSpec) -> Callable[[type[BaseEngine]], type[BaseEngine]]:
    """Decorator used by business modules to register engine classes."""
    def decorator(engine_cls: type[BaseEngine]) -> type[BaseEngine]:
        engine_cls.SPEC = spec
        return EngineRegistry.register(spec, engine_cls)

    return decorator


class EngineManager:
    """Per-domain helper that selects, creates, and switches engines."""
    def __init__(
        self,
        domain: str,
        engine_name: str,
        *,
        config: EngineConfig | dict[str, Any] | None = None,
        registry: type[EngineRegistry] = EngineRegistry,
    ):
        self.domain = domain
        self.engine_name = engine_name
        self.registry = registry
        self.config = EngineConfig.from_value(config)
        self._metrics: dict[tuple[str, str], EngineMetricsSnapshot] = {}

    def list_engines(self) -> list[EngineSpec]:
        """List available engines for the current domain."""
        return self.registry.list(domain=self.domain)

    def refresh(self) -> list[EngineSpec]:
        """Refresh entry-point registrations and return engines for this domain."""
        refreshed = self.registry.refresh_entry_points()
        return [spec for spec in refreshed if spec.domain == self.domain]

    def switch_engine(
        self,
        engine_name: str,
        *,
        config: EngineConfig | dict[str, Any] | None = None,
    ) -> None:
        """Switch the selected engine for future instances."""
        previous_key = (self.domain, self.engine_name)
        metrics = self._metrics.get(previous_key)
        if metrics is not None:
            metrics.switch_count += 1
        self.engine_name = engine_name
        if config is not None:
            self.config = EngineConfig.from_value(config)

    def create_engine(
        self,
        *,
        context: EngineContext | None = None,
        config: EngineConfig | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> BaseEngine:
        """Instantiate the currently selected engine."""
        engine_cls = self.registry.get(self.domain, self.engine_name)
        engine = engine_cls(
            context=context,
            config=EngineConfig.from_value(config) if config is not None else self.config,
            **kwargs,
        )
        self._metrics[(self.domain, self.engine_name)] = engine.get_metrics_snapshot()
        return engine

    def get_current_spec(self) -> EngineSpec:
        """Return the spec of the currently selected engine."""
        return self.registry.get_spec(self.domain, self.engine_name)

    def get_metrics(self) -> dict[str, Any]:
        """Return metrics collected from engines created by this manager."""
        return {
            f"{domain}:{name}": snapshot.to_dict()
            for (domain, name), snapshot in self._metrics.items()
        }
