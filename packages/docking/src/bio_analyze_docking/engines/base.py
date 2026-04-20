from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseDockingEngine(ABC):
    """
    Abstract base class for docking engines.

    All docking engines should inherit from this class and implement abstract methods.
    """

    def __init__(self, receptor: Path, ligand: Path, output_dir: Path):
        """
        Initialize the docking engine.

        Args:
            receptor (Path):
                Path to the receptor file
            ligand (Path):
                Path to the ligand file
            output_dir (Path):
                Path to the output directory
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
        Get the expected receptor file extension for this engine.
        """
        return ".pdbqt"

    @classmethod
    def get_ligand_ext(cls) -> str:
        """
        Get the expected ligand file extension for this engine.
        """
        return ".pdbqt"

    @classmethod
    def get_output_ext(cls) -> str:
        """
        Get the output file extension for this engine.
        """
        return ".pdbqt"

    @classmethod
    def prepare_receptor(cls, input_file: Path, output_file: Path, **kwargs) -> Path:
        """
        Prepare the receptor file for the current engine.
        """
        # 默认实现：直接返回输入路径，或由子类覆盖
        return Path(input_file)

    @classmethod
    def prepare_ligand(cls, input_file: Path, output_file: Path, **kwargs) -> Path:
        """
        Prepare the ligand file for the current engine.
        """
        # 默认实现：直接返回输入路径，或由子类覆盖
        return Path(input_file)

    @classmethod
    def get_summary_config(cls) -> dict[str, str]:
        """
        Get the summary configuration map {display_name: internal_key}.
        """
        return {
            "Affinity (kcal/mol)": "affinity",
            "RMSD l.b.": "rmsd_lb",
            "RMSD u.b.": "rmsd_ub",
        }

    @abstractmethod
    def compute_box(self, center: list[float], size: list[float]):
        """
        Define the search space (grid box).

        Args:
            center (list[float]):
                [x, y, z] center coordinates (Angstroms)
            size (list[float]):
                [x, y, z] box dimensions (Angstroms)
        """
        pass

    @abstractmethod
    def dock(self, exhaustiveness: int = 8, n_poses: int = 9, min_rmsd: float = 1.0, timeout: float = 3600):
        """
        Perform docking.

        Args:
            exhaustiveness (int, optional):
                Search exhaustiveness
            n_poses (int, optional):
                Number of poses to generate
            min_rmsd (float, optional):
                Minimum RMSD threshold
            timeout (float, optional):
                Timeout in seconds
        """
        pass

    @abstractmethod
    def save_results(self, output_name: str = "docked.pdbqt", output_dir: Path | None = None) -> Path:
        """
        Save docked poses.

        Args:
            output_name (str, optional):
                Output filename
            output_dir (Optional[Path], optional):
                Output directory path. If None, uses the output_dir from initialization.

        Returns:
            Path:
                Path to the saved result file
        """
        pass

    @abstractmethod
    def save_complexes(
        self,
        n_complexes: int | None = None,
        output_dir: Path | None = None,
        output_name_prefix: str = "complex_pose",
    ):
        """
        Save the docked ligand-receptor complex structures.

        Args:
            n_complexes (Optional[int], optional):
                Number of complexes to save. If None, saves all.
            output_dir (Optional[Path], optional):
                Output directory path. If None, uses the output_dir from initialization.
            output_name_prefix (str, optional):
                Prefix for output filenames (default is "complex_pose").
        """
        pass

    @abstractmethod
    def score(self) -> float:
        """
        Get the best energy score (kcal/mol).

        Returns:
            float:
                Best energy score
        """
        pass

    @abstractmethod
    def get_all_poses_info(self, n_poses: int = 9) -> list[dict[str, Any]]:
        """
        Get information for all poses: energy, RMSD lower bound, RMSD upper bound.

        Args:
            n_poses (int, optional):
                Number of poses to get information for

        Returns:
            list[dict[str, Any]]:
                List of dictionaries containing pose information
        """
        pass
