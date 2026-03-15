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
    def create_engine(
        cls, engine_type: str, receptor_pdbqt: Path, ligand_pdbqt: Path, output_dir: Path
    ) -> BaseDockingEngine:
        """
        zh: 创建一个对接引擎实例。
        en: Create a docking engine instance.

        Args:
            engine_type (str):
                zh: 引擎类型（例如 "vina"）
                en: Engine type (e.g., "vina")
            receptor_pdbqt (Path):
                zh: 受体 PDBQT 文件路径
                en: Path to the receptor PDBQT file
            ligand_pdbqt (Path):
                zh: 配体 PDBQT 文件路径
                en: Path to the ligand PDBQT file
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
        engine_class = cls._engines.get(engine_type.lower())
        if not engine_class:
            raise ValueError(f"不支持的对接引擎类型: {engine_type}。可用引擎: {list(cls._engines.keys())}")

        return engine_class(receptor_pdbqt, ligand_pdbqt, output_dir)

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
