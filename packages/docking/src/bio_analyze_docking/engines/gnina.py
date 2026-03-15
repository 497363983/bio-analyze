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


class GninaEngine(BaseDockingEngine):
    """
    zh: 基于 Gnina 的对接引擎实现。
    en: Gnina-based docking engine implementation.

    zh: Gnina 是 Smina 的一个分支，集成了深度学习评分函数 (CNN scoring)。
    en: Gnina is a fork of Smina that integrates deep learning scoring functions (CNN scoring).
    zh: 本引擎通过 subprocess 调用 gnina 命令行工具。
    en: This engine invokes the gnina command-line tool via subprocess.
    """

    def __init__(self, receptor_pdbqt: Path, ligand_pdbqt: Path, output_dir: Path):
        """
        zh: 初始化 Gnina 对接引擎。
        en: Initialize the Gnina docking engine.
        """
        super().__init__(receptor_pdbqt, ligand_pdbqt, output_dir)

        # 检查 gnina 是否可用
        self.gnina_executable = shutil.which("gnina")
        if self.gnina_executable is None:
            # 尝试在当前目录下查找
            if (Path.cwd() / "gnina").exists():
                self.gnina_executable = str(Path.cwd() / "gnina")
            elif (Path.cwd() / "gnina.exe").exists():
                self.gnina_executable = str(Path.cwd() / "gnina.exe")

        if self.gnina_executable is None:
            raise RuntimeError("未在 PATH 中找到 'gnina' 可执行文件。请确保已安装 gnina 并将其添加到系统路径中。")

        self.box_center = None
        self.box_size = None
        self._temp_output_file = self.output_dir / "gnina_out.pdbqt"
        self._last_exhaustiveness = 8
        self._last_n_poses = 9
        self._last_min_rmsd = 1.0

    def compute_box(self, center: list[float], size: list[float]):
        """
        zh: 定义搜索空间（网格盒）。
        en: Define the search space (grid box).
        """
        logger.info(f"设置 Gnina 搜索盒子 (中心={center}, 尺寸={size})...")
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
            self.gnina_executable,
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
            "--min_rmsd",
            str(min_rmsd),
            "--out",
            str(self._temp_output_file),
            "--cpu",
            "1",  # 默认使用单核，可以通过其他方式配置
        ]

        # 增加 cpu 参数支持，如果有 multiprocessing
        import multiprocessing

        try:
            cpu_count = multiprocessing.cpu_count()
            # 更新 cpu 参数
            cmd_args[-1] = str(cpu_count)
        except Exception:
            pass

        logger.info(f"执行 Gnina 命令: {' '.join(cmd_args)}")

        try:
            result = subprocess.run(cmd_args, capture_output=True, text=True, check=True, encoding="utf-8")
            logger.debug(f"Gnina 输出:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Gnina 执行失败: {e.stderr}")
            raise RuntimeError(f"Gnina 对接失败: {e.stderr}")

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
        zh: 返回所有姿态的信息：能量，RMSD 下界，RMSD 上界，以及 CNN 评分。
        en: Return information for all poses: energy, RMSD lower bound, RMSD upper bound, and CNN score.

        zh: 从 PDBQT 输出文件中解析。
        en: Parsed from the PDBQT output file.
        """
        if not self._temp_output_file.exists():
            return []

        results = []
        # Gnina 输出格式示例：
        # REMARK VINA RESULT:    -7.8      0.000      0.000
        # REMARK CNNscore: 0.9876
        # REMARK CNNaffinity: 8.1234
        # REMARK minimized affinity -7.82134

        vina_pattern = re.compile(r"REMARK VINA RESULT:\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")
        cnn_score_pattern = re.compile(r"REMARK CNNscore:\s+([-\d.]+)")
        cnn_affinity_pattern = re.compile(r"REMARK CNNaffinity:\s+([-\d.]+)")

        try:
            with open(self._temp_output_file, encoding="utf-8") as f:
                lines = f.readlines()

            current_pose = {}
            pose_idx = 0
            in_model = False

            for line in lines:
                if line.startswith("MODEL"):
                    pose_idx += 1
                    current_pose = {"pose": pose_idx}
                    in_model = True

                elif in_model:
                    if line.startswith("REMARK VINA RESULT:"):
                        match = vina_pattern.search(line)
                        if match:
                            current_pose["affinity"] = float(match.group(1))
                            current_pose["rmsd_lb"] = float(match.group(2))
                            current_pose["rmsd_ub"] = float(match.group(3))

                    elif line.startswith("REMARK CNNscore:"):
                        match = cnn_score_pattern.search(line)
                        if match:
                            current_pose["cnn_score"] = float(match.group(1))

                    elif line.startswith("REMARK CNNaffinity:"):
                        match = cnn_affinity_pattern.search(line)
                        if match:
                            current_pose["cnn_affinity"] = float(match.group(1))

                    elif line.startswith("ENDMDL"):
                        if "affinity" in current_pose:
                            results.append(current_pose)
                            if len(results) >= n_poses:
                                break
                        in_model = False

        except Exception as e:
            logger.error(f"解析 Gnina 结果文件失败: {e}")
            return []

        return results
