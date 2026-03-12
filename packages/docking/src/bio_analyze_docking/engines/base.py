from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class BaseDockingEngine(ABC):
    """
    对接引擎的抽象基类。
    所有对接引擎都应继承此类并实现抽象方法。
    """

    def __init__(self, receptor_pdbqt: Path, ligand_pdbqt: Path, output_dir: Path):
        """
        初始化对接引擎。

        Args:
            receptor_pdbqt: 受体 PDBQT 文件路径
            ligand_pdbqt: 配体 PDBQT 文件路径
            output_dir: 输出目录路径
        """
        self.receptor = Path(receptor_pdbqt)
        self.ligand = Path(ligand_pdbqt)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.receptor.exists():
            raise FileNotFoundError(f"受体文件未找到: {self.receptor}")
        if not self.ligand.exists():
            raise FileNotFoundError(f"配体文件未找到: {self.ligand}")

    @abstractmethod
    def compute_box(self, center: list[float], size: list[float]):
        """
        定义搜索空间（网格盒）。

        Args:
            center: [x, y, z] 中心坐标（埃）
            size: [x, y, z] 盒子尺寸（埃）
        """
        pass

    @abstractmethod
    def dock(self, exhaustiveness: int = 8, n_poses: int = 9, min_rmsd: float = 1.0):
        """
        执行对接。

        Args:
            exhaustiveness: 搜索详尽程度
            n_poses: 生成的姿态数量
            min_rmsd: 最小 RMSD 阈值
        """
        pass

    @abstractmethod
    def save_results(self, output_name: str = "docked.pdbqt", output_dir: Optional[Path] = None) -> Path:
        """
        保存对接姿态。

        Args:
            output_name: 输出文件名
            output_dir: 输出目录路径。如果为 None，则使用初始化时的 output_dir。

        Returns:
            Path: 保存的结果文件路径
        """
        pass

    @abstractmethod
    def save_complexes(
        self,
        n_complexes: Optional[int] = None,
        output_dir: Optional[Path] = None,
        output_name_prefix: str = "complex_pose",
    ):
        """
        保存对接后的复合物结构。

        Args:
            n_complexes: 要保存的复合物数量。如果为 None，则保存所有。
            output_dir: 输出目录路径。如果为 None，则使用初始化时的 output_dir。
            output_name_prefix: 输出文件名的前缀 (默认为 "complex_pose")。
        """
        pass

    @abstractmethod
    def score(self) -> float:
        """
        获取最佳能量评分（kcal/mol）。

        Returns:
            float: 最佳能量评分
        """
        pass

    @abstractmethod
    def get_all_poses_info(self, n_poses: int = 9) -> list[dict[str, Any]]:
        """
        获取所有姿态的信息：能量，RMSD 下界，RMSD 上界。

        Args:
            n_poses: 要获取信息的姿态数量

        Returns:
            List[Dict[str, Any]]: 包含姿态信息的字典列表
        """
        pass
