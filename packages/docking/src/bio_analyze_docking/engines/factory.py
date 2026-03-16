from __future__ import annotations

from pathlib import Path

from .base import BaseDockingEngine
from .gnina import GninaEngine
from .smina import SminaEngine
from .vina import VinaEngine


class DockingEngineFactory:
    """
    zh: 对接引擎工厂类。
    en: Docking engine factory class.

    zh: 用于根据名称创建特定的对接引擎实例。
    en: Used to create specific docking engine instances based on name.
    """

    _engines: dict[str, type[BaseDockingEngine]] = {
        "vina": VinaEngine,
        "smina": SminaEngine,
        "gnina": GninaEngine,
    }

    @classmethod
    def get_engine_class(cls, engine_type: str) -> type[BaseDockingEngine]:
        """
        zh: 获取对接引擎类，而不实例化它。
        en: Get the docking engine class without instantiating it.
        """
        engine_class = cls._engines.get(engine_type.lower())
        if not engine_class:
            raise ValueError(f"不支持的对接引擎类型: {engine_type}。可用引擎: {list(cls._engines.keys())}")
        return engine_class

    @classmethod
    def create_engine(
        cls, engine_type: str, receptor: Path, ligand: Path, output_dir: Path
    ) -> BaseDockingEngine:
        """
        zh: 创建一个对接引擎实例。
        en: Create a docking engine instance.

        Args:
            engine_type (str):
                zh: 引擎类型（例如 "vina"）
                en: Engine type (e.g., "vina")
            receptor (Path):
                zh: 受体文件路径
                en: Path to the receptor file
            ligand (Path):
                zh: 配体文件路径
                en: Path to the ligand file
            output_dir (Path):
                zh: 输出目录路径
                en: Path to the output directory

        Returns:
            BaseDockingEngine:
                zh: 对接引擎实例
                en: Docking engine instance

        Raises:
            ValueError:
                zh: 如果引擎类型不受支持
                en: If the engine type is not supported
        """
        engine_class = cls.get_engine_class(engine_type)
        return engine_class(receptor, ligand, output_dir)

    @classmethod
    def register_engine(cls, name: str, engine_class: type[BaseDockingEngine]):
        """
        zh: 注册一个新的对接引擎。
        en: Register a new docking engine.

        Args:
            name (str):
                zh: 引擎名称
                en: Engine name
            engine_class (type[BaseDockingEngine]):
                zh: 引擎类
                en: Engine class
        """
        cls._engines[name.lower()] = engine_class
