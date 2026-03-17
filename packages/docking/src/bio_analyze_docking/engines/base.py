from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class BaseDockingEngine(ABC):
    """
    zh: 对接引擎的抽象基类。
    en: Abstract base class for docking engines.

    zh: 所有对接引擎都应继承此类并实现抽象方法。
    en: All docking engines should inherit from this class and implement abstract methods.
    """

    def __init__(self, receptor: Path, ligand: Path, output_dir: Path):
        """
        zh: 初始化对接引擎。
        en: Initialize the docking engine.

        Args:
            receptor (Path):
                zh: 受体文件路径
                en: Path to the receptor file
            ligand (Path):
                zh: 配体文件路径
                en: Path to the ligand file
            output_dir (Path):
                zh: 输出目录路径
                en: Path to the output directory
        """
        self.receptor = Path(receptor)
        self.ligand = Path(ligand)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.receptor.exists():
            raise FileNotFoundError(f"受体文件未找到: {self.receptor}")
        if not self.ligand.exists():
            raise FileNotFoundError(f"配体文件未找到: {self.ligand}")

    @classmethod
    def get_receptor_ext(cls) -> str:
        """
        zh: 获取引擎期望的受体文件扩展名。
        en: Get the expected receptor file extension for this engine.
        """
        return ".pdbqt"

    @classmethod
    def get_ligand_ext(cls) -> str:
        """
        zh: 获取引擎期望的配体文件扩展名。
        en: Get the expected ligand file extension for this engine.
        """
        return ".pdbqt"

    @classmethod
    def get_output_ext(cls) -> str:
        """
        zh: 获取引擎输出结果的文件扩展名。
        en: Get the output file extension for this engine.
        """
        return ".pdbqt"

    @classmethod
    def prepare_receptor(cls, input_file: Path, output_file: Path, **kwargs) -> Path:
        """
        zh: 准备受体文件以供当前引擎使用。
        en: Prepare the receptor file for the current engine.
        """
        # 默认实现：直接返回输入路径，或由子类覆盖
        return Path(input_file)

    @classmethod
    def prepare_ligand(cls, input_file: Path, output_file: Path, **kwargs) -> Path:
        """
        zh: 准备配体文件以供当前引擎使用。
        en: Prepare the ligand file for the current engine.
        """
        # 默认实现：直接返回输入路径，或由子类覆盖
        return Path(input_file)

    @classmethod
    def get_summary_config(cls) -> dict[str, str]:
        """
        zh: 获取结果摘要的配置映射 {显示名称: 内部键名}。
        en: Get the summary configuration map {display_name: internal_key}.
        """
        return {
            "Affinity (kcal/mol)": "affinity",
            "RMSD l.b.": "rmsd_lb",
            "RMSD u.b.": "rmsd_ub",
        }

    @abstractmethod
    def compute_box(self, center: list[float], size: list[float]):
        """
        zh: 定义搜索空间（网格盒）。
        en: Define the search space (grid box).

        Args:
            center (list[float]):
                zh: [x, y, z] 中心坐标（埃）
                en: [x, y, z] center coordinates (Angstroms)
            size (list[float]):
                zh: [x, y, z] 盒子尺寸（埃）
                en: [x, y, z] box dimensions (Angstroms)
        """
        pass

    @abstractmethod
    def dock(self, exhaustiveness: int = 8, n_poses: int = 9, min_rmsd: float = 1.0):
        """
        zh: 执行对接。
        en: Perform docking.

        Args:
            exhaustiveness (int, optional):
                zh: 搜索详尽程度
                en: Search exhaustiveness
            n_poses (int, optional):
                zh: 生成的姿态数量
                en: Number of poses to generate
            min_rmsd (float, optional):
                zh: 最小 RMSD 阈值
                en: Minimum RMSD threshold
        """
        pass

    @abstractmethod
    def save_results(self, output_name: str = "docked.pdbqt", output_dir: Optional[Path] = None) -> Path:
        """
        zh: 保存对接姿态。
        en: Save docked poses.

        Args:
            output_name (str, optional):
                zh: 输出文件名
                en: Output filename
            output_dir (Optional[Path], optional):
                zh: 输出目录路径。如果为 None，则使用初始化时的 output_dir。
                en: Output directory path. If None, uses the output_dir from initialization.

        Returns:
            Path:
                zh: 保存的结果文件路径
                en: Path to the saved result file
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
        zh: 保存对接后的复合物结构。
        en: Save the docked ligand-receptor complex structures.

        Args:
            n_complexes (Optional[int], optional):
                zh: 要保存的复合物数量。如果为 None，则保存所有。
                en: Number of complexes to save. If None, saves all.
            output_dir (Optional[Path], optional):
                zh: 输出目录路径。如果为 None，则使用初始化时的 output_dir。
                en: Output directory path. If None, uses the output_dir from initialization.
            output_name_prefix (str, optional):
                zh: 输出文件名的前缀 (默认为 "complex_pose")。
                en: Prefix for output filenames (default is "complex_pose").
        """
        pass

    @abstractmethod
    def score(self) -> float:
        """
        zh: 获取最佳能量评分（kcal/mol）。
        en: Get the best energy score (kcal/mol).

        Returns:
            float:
                zh: 最佳能量评分
                en: Best energy score
        """
        pass

    @abstractmethod
    def get_all_poses_info(self, n_poses: int = 9) -> list[dict[str, Any]]:
        """
        zh: 获取所有姿态的信息：能量，RMSD 下界，RMSD 上界。
        en: Get information for all poses: energy, RMSD lower bound, RMSD upper bound.

        Args:
            n_poses (int, optional):
                zh: 要获取信息的姿态数量
                en: Number of poses to get information for

        Returns:
            list[dict[str, Any]]:
                zh: 包含姿态信息的字典列表
                en: List of dictionaries containing pose information
        """
        pass
