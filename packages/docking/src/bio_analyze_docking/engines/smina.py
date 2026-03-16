from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

from bio_analyze_core.logging import get_logger

from ..utils import merge_complex_with_pymol
from .base import BaseDockingEngine

try:
    from pymol import cmd
except ImportError:
    cmd = None

logger = get_logger(__name__)


class SminaEngine(BaseDockingEngine):
    """
    zh: 基于 Smina 的对接引擎实现。
    en: Smina-based docking engine implementation.

    zh: Smina 是 Vina 的一个分支，提供了更好的评分函数和更多功能。
    en: Smina is a fork of Vina that provides better scoring functions and more features.
    zh: 本引擎通过 subprocess 调用 smina 命令行工具。
    en: This engine invokes the smina command-line tool via subprocess.
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
        zh: 初始化 Smina 对接引擎。
        en: Initialize the Smina docking engine.
        """
        super().__init__(receptor, ligand, output_dir)

        # 检查 smina 是否可用
        self.smina_executable = shutil.which("smina")
        if self.smina_executable is None:
            # 尝试在当前目录下查找（Windows环境可能）
            if (Path.cwd() / "smina.exe").exists():
                self.smina_executable = str(Path.cwd() / "smina.exe")
            else:
                # 尝试常见的别名或路径? 暂时只检查 PATH
                pass

        if self.smina_executable is None:
            raise RuntimeError("未在 PATH 中找到 'smina' 可执行文件。请确保已安装 smina 并将其添加到系统路径中。")

        self.box_center = None
        self.box_size = None
        self._temp_output_file = self.output_dir / "smina_out.pdbqt"
        self._last_exhaustiveness = 8
        self._last_n_poses = 9
        self._last_min_rmsd = 1.0

    def compute_box(self, center: list[float], size: list[float]):
        """
        zh: 定义搜索空间（网格盒）。
        en: Define the search space (grid box).
        """
        logger.info(f"设置 Smina 搜索盒子 (中心={center}, 尺寸={size})...")
        self.box_center = center
        self.box_size = size

    def dock(self, exhaustiveness: int = 8, n_poses: int = 9, min_rmsd: float = 1.0):
        """
        zh: 执行对接。
        en: Perform docking.
        """
        if self.box_center is None or self.box_size is None:
            raise RuntimeError("在执行对接前必须先调用 compute_box 设置搜索空间。")

        self._last_exhaustiveness = exhaustiveness
        self._last_n_poses = n_poses
        self._last_min_rmsd = min_rmsd

        cmd_args = [
            self.smina_executable,
            "--receptor",
            str(self.receptor),
            "--ligand",
            str(self.ligand),
            "--center_x",
            str(self.box_center[0]),
            "--center_y",
            str(self.box_center[1]),
            "--center_z",
            str(self.box_center[2]),
            "--size_x",
            str(self.box_size[0]),
            "--size_y",
            str(self.box_size[1]),
            "--size_z",
            str(self.box_size[2]),
            "--exhaustiveness",
            str(exhaustiveness),
            "--num_modes",
            str(n_poses),
            "--min_rmsd_filter", # Smina uses min_rmsd_filter not min_rmsd
            str(min_rmsd),
            "--out",
            str(self._temp_output_file),
            "--cpu",
            "1",  # 默认使用单核，可以通过其他方式配置? 暂时硬编码或从环境获取
        ]

        # 增加 cpu 参数支持，如果有 multiprocessing
        import multiprocessing

        try:
            cpu_count = multiprocessing.cpu_count()
            # 更新 cpu 参数
            cmd_args[-1] = str(cpu_count)
        except Exception:
            pass

        logger.info(f"执行 Smina 命令: {' '.join(cmd_args)}")

        try:
            result = subprocess.run(cmd_args, capture_output=True, text=True, check=True, encoding="utf-8")
            logger.debug(f"Smina 输出:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Smina 执行失败: {e.stderr}")
            raise RuntimeError(f"Smina 对接失败: {e.stderr}")

    def save_results(self, output_name: str = "docked.pdbqt", output_dir: Optional[Path] = None) -> Path:
        """
        zh: 保存对接姿态。
        en: Save docked poses.

        zh: 实际上是将临时输出文件复制到目标位置。
        en: Actually copies the temporary output file to the target location.
        """
        if not self._temp_output_file.exists():
            raise RuntimeError("未找到对接结果文件。请先运行 dock()。")

        target_dir = output_dir if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = target_dir / output_name

        logger.info(f"保存对接姿态到: {out_path}")
        shutil.copy2(self._temp_output_file, out_path)
        return out_path

    def save_complexes(
        self,
        n_complexes: Optional[int] = None,
        output_dir: Optional[Path] = None,
        output_name_prefix: str = "complex_pose",
    ):
        """
        zh: 使用 PyMOL 将对接的配体-受体复合物保存为 PDB 文件。
        en: Save the docked ligand-receptor complex as a PDB file using PyMOL.
        """
        if cmd is None:
            logger.error("PyMOL 未安装。无法保存 PDB 复合物。")
            return

        target_dir = output_dir if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        if not self._temp_output_file.exists():
            logger.warning("未找到对接结果，无法保存复合物。")
            return

        # 解析结果数量
        poses_info = self.get_all_poses_info(n_poses=999)
        total_poses = len(poses_info)

        if total_poses == 0:
            logger.warning("对接结果为空，无法保存复合物。")
            return

        n_save = total_poses
        if n_complexes is not None:
            n_save = min(n_complexes, total_poses)

        logger.info(f"保存 {n_save} 个对接复合物 (PDB 格式) 到 {target_dir}...")

        try:
            merge_complex_with_pymol(self.receptor, self._temp_output_file, target_dir, n_save, output_name_prefix)

        except Exception as e:
            logger.error(f"使用 PyMOL 生成复合物 PDB 失败: {e}")
            # finally 块中的清理工作由 merge_complex_with_pymol 处理一部分，但这里我们也需要清理
        finally:
            if cmd is not None:
                cmd.reinitialize()

    def score(self) -> float:
        """
        zh: 返回最佳能量评分（kcal/mol）。
        en: Return the best energy score (kcal/mol).
        """
        if not self._temp_output_file.exists():
            return 0.0

        poses = self.get_all_poses_info(n_poses=1)
        if poses:
            return poses[0]["affinity"]
        return 0.0

    def get_all_poses_info(self, n_poses: int = 9) -> list[dict[str, Any]]:
        """
        zh: 返回所有姿态的信息：能量，RMSD 下界，RMSD 上界。
        en: Return information for all poses: energy, RMSD lower bound, RMSD upper bound.

        zh: 从 PDBQT 输出文件中解析。
        en: Parsed from the PDBQT output file.
        """
        if not self._temp_output_file.exists():
            return []

        results = []
        # REMARK VINA RESULT:    -8.5      0.000      0.000
        # smina 输出格式与 vina 类似
        # REMARK minimized affinity -8.54848 (kcal/mol)
        # 或者兼容模式
        # 让我们检查 smina 的标准输出 PDBQT

        # 标准 Vina 输出:
        # REMARK VINA RESULT:    -9.3      0.000      0.000

        # Smina 默认似乎也保持这个格式，或者是:
        # REMARK minimized affinity <val>

        # 我们可以尝试匹配这两种格式
        vina_pattern = re.compile(r"REMARK VINA RESULT:\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")

        try:
            with open(self._temp_output_file, encoding="utf-8") as f:
                pose_idx = 1
                for line in f:
                    if line.startswith("REMARK VINA RESULT:"):
                        match = vina_pattern.search(line)
                        if match:
                            affinity = float(match.group(1))
                            rmsd_lb = float(match.group(2))
                            rmsd_ub = float(match.group(3))

                            results.append(
                                {"pose": pose_idx, "affinity": affinity, "rmsd_lb": rmsd_lb, "rmsd_ub": rmsd_ub}
                            )
                            pose_idx += 1

                            if len(results) >= n_poses:
                                break
        except Exception as e:
            logger.error(f"解析 Smina 结果文件失败: {e}")
            return []

        return results
