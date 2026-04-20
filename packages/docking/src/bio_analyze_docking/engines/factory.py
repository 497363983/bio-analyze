from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from bio_analyze_core.engine import EngineRegistry, EngineSpec

from .base import BaseDockingEngine
from .gnina import GninaEngine
from .haddock import HaddockEngine
from .smina import SminaEngine
from .vina import VinaEngine


class DockingEngineFactory:
    """
    Docking engine factory class.

    Used to create specific docking engine instances based on name.
    """

    _engines: ClassVar[dict[str, type[BaseDockingEngine]]] = {
        "vina": VinaEngine,
        "smina": SminaEngine,
        "gnina": GninaEngine,
        "haddock": HaddockEngine,
    }

    @classmethod
    def _sync_registry(cls) -> None:
        for name, engine_class in cls._engines.items():
            EngineRegistry.register(EngineSpec(domain="docking", name=name), engine_class)

    @classmethod
    def get_engine_class(cls, engine_type: str) -> type[BaseDockingEngine]:
        """
        Get the docking engine class without instantiating it.
        """
        normalized_name = engine_type.lower()
        cls._sync_registry()
        engine_class = cls._engines.get(normalized_name)
        if not engine_class:
            try:
                engine_class = EngineRegistry.get("docking", normalized_name)
            except ValueError as exc:
                raise ValueError(
                    f"不支持的对接引擎类型: {engine_type}。可用引擎: {list(cls._engines.keys())}"
                ) from exc
        if not engine_class:
            raise ValueError(f"不支持的对接引擎类型: {engine_type}。可用引擎: {list(cls._engines.keys())}")
        return engine_class

    @classmethod
    def create_engine(cls, engine_type: str, receptor: Path, ligand: Path, output_dir: Path) -> BaseDockingEngine:
        """
        Create a docking engine instance.

        Args:
            engine_type (str):
                Engine type (e.g., "vina")
            receptor (Path):
                Path to the receptor file
            ligand (Path):
                Path to the ligand file
            output_dir (Path):
                Path to the output directory

        Returns:
            BaseDockingEngine:
                Docking engine instance

        Raises:
            ValueError:
                If the engine type is not supported
        """
        engine_class = cls.get_engine_class(engine_type)
        return engine_class(receptor, ligand, output_dir)

    @classmethod
    def register_engine(cls, name: str, engine_class: type[BaseDockingEngine]):
        """
        Register a new docking engine.

        Args:
            name (str):
                Engine name
            engine_class (type[BaseDockingEngine]):
                Engine class
        """
        normalized_name = name.lower()
        cls._engines[normalized_name] = engine_class
        EngineRegistry.register(EngineSpec(domain="docking", name=normalized_name), engine_class)
