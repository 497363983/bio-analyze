from __future__ import annotations

from pathlib import Path

from .base import BaseDockingEngine
from .gnina import GninaEngine
from .smina import SminaEngine
from .vina import VinaEngine


class DockingEngineFactory:
    """
    对接引擎工厂类。
    用于根据名称创建特定的对接引擎实例。
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
        创建一个对接引擎实例。

        Args:
            engine_type: 引擎类型（例如 "vina"）
            receptor_pdbqt: 受体 PDBQT 文件路径
            ligand_pdbqt: 配体 PDBQT 文件路径
            output_dir: 输出目录路径

        Returns:
            BaseDockingEngine: 对接引擎实例

        Raises:
            ValueError: 如果引擎类型不受支持
        """
        engine_class = cls._engines.get(engine_type.lower())
        if not engine_class:
            raise ValueError(f"不支持的对接引擎类型: {engine_type}。可用引擎: {list(cls._engines.keys())}")

        return engine_class(receptor_pdbqt, ligand_pdbqt, output_dir)

    @classmethod
    def register_engine(cls, name: str, engine_class: type[BaseDockingEngine]):
        """
        注册一个新的对接引擎。

        Args:
            name: 引擎名称
            engine_class: 引擎类
        """
        cls._engines[name.lower()] = engine_class
