from __future__ import annotations

from pathlib import Path
from typing import Any

from bio_analyze_core.logging import get_logger

try:
    from vina import Vina
except ImportError:
    Vina = None

try:
    from pymol import cmd
except ImportError:
    cmd = None

from ..utils import merge_complex_with_pymol
from .base import BaseDockingEngine

logger = get_logger(__name__)

class VinaEngine(BaseDockingEngine):
    """
    Vina-based docking engine implementation.
    """

    @classmethod
    def prepare_receptor(cls, input_file: Path, output_file: Path, **kwargs) -> Path:
        from ..prep import prepare_receptor as prep_rec

        return prep_rec(input_file, output_file, **kwargs)

    @classmethod
    def prepare_ligand(cls, input_file: Path, output_file: Path, **kwargs) -> Path:
        from ..prep import prepare_ligand as prep_lig

        return prep_lig(input_file, output_file, **kwargs)

    def __init__(self, receptor: Path, ligand: Path, output_dir: Path):
        """
        Initialize the Vina docking engine.
        """
        if Vina is None:
            raise ImportError("Vina module not found. Please install vina to use VinaEngine.")

        # if cmd is None:
        #     logger.warning("PyMOL module not found. save_complexes will not work.")

        super().__init__(receptor, ligand, output_dir)
        self.engine = Vina(sf_name="vina")

        # 加载受体
        logger.info(f"加载受体: {self.receptor.name}")
        self.engine.set_receptor(str(self.receptor))

        # 加载配体
        logger.info(f"加载配体: {self.ligand.name}")
        self.engine.set_ligand_from_file(str(self.ligand))

    def compute_box(self, center: list[float], size: list[float]):
        """
        Define the search space (grid box).

        Args:
            center (list[float]):
                [x, y, z] center coordinates (Angstroms)
            size (list[float]):
                [x, y, z] box dimensions (Angstroms)
        """
        logger.info(f"计算 Vina 映射 (中心={center}, 尺寸={size})...")
        self.engine.compute_vina_maps(center=center, box_size=size)

    def dock(self, exhaustiveness: int = 8, n_poses: int = 9, min_rmsd: float = 1.0, timeout: float = 3600):
        """
        Perform docking.
        """
        logger.info(f"开始对接 (搜索深度={exhaustiveness})...")
        self.engine.dock(exhaustiveness=exhaustiveness, n_poses=n_poses, min_rmsd=min_rmsd)

    def save_results(self, output_name: str = "docked.pdbqt", output_dir: Path | None = None) -> Path:
        """
        Save docked poses.
        """
        target_dir = output_dir if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = target_dir / output_name

        logger.info(f"保存对接姿态到: {out_path}")
        self.engine.write_poses(str(out_path), n_poses=9, overwrite=True)
        return out_path

    def save_complexes(
        self,
        n_complexes: int | None = None,
        output_dir: Path | None = None,
        output_name_prefix: str = "complex_pose",
    ):
        """
        Save the docked ligand-receptor complex as a PDB file using PyMOL.

        Args:
            n_complexes (Optional[int], optional):
                Number of top complexes to save. If None, saves all.
            output_dir (Optional[Path], optional):
                Output directory. If None, uses the output_dir from initialization.
            output_name_prefix (str, optional):
                Prefix for output filenames (default is "complex_pose").
        """
        if cmd is None:
            logger.error("PyMOL 未安装。无法保存 PDB 复合物。")
            return

        target_dir = output_dir if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        # 确保我们有对接结果
        energies = self.engine.energies(n_poses=999)  # 获取所有可用的结果
        if len(energies) == 0:
            logger.warning("未找到对接结果, 无法保存复合物。")
            return

        total_poses = len(energies)
        n_save = total_poses
        if n_complexes is not None:
            n_save = min(n_complexes, total_poses)

        logger.info(f"保存 {n_save} 个对接复合物 (PDB 格式) 到 {target_dir}...")

        # 将姿态写入临时文件
        temp_poses = self.output_dir / "temp_poses.pdbqt"
        self.engine.write_poses(str(temp_poses), n_poses=n_save, overwrite=True)

        try:
            merge_complex_with_pymol(self.receptor, temp_poses, target_dir, n_save, output_name_prefix)

        except Exception as e:
            logger.error(f"使用 PyMOL 生成复合物 PDB 失败: {e}")
        finally:
            if temp_poses.exists():
                temp_poses.unlink()
            # 清理 PyMOL 会话
            cmd.reinitialize()

    def score(self) -> float:
        """
        Return the best energy score (kcal/mol).
        """
        energies = self.engine.energies(n_poses=1)
        if len(energies) > 0:
            return energies[0][0]
        return 0.0

    def get_all_poses_info(self, n_poses: int = 9) -> list[dict[str, Any]]:
        """
        Return information for all poses: energy, RMSD lower bound, RMSD upper bound.
        """
        # energies() 返回每个姿态的 [affinity, rmsd_lb, rmsd_ub] 列表
        energies = self.engine.energies(n_poses=n_poses)
        results = []
        if len(energies) > 0:
            for i, e in enumerate(energies):
                results.append({"pose": i + 1, "affinity": e[0], "rmsd_lb": e[1], "rmsd_ub": e[2]})
        return results
