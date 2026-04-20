from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import CalledProcessError
from bio_analyze_core.subprocess import run as run_command

from ..utils import merge_complex_with_pymol
from .base import BaseDockingEngine

try:
    from pymol import cmd
except ImportError:
    cmd = None

logger = get_logger(__name__)

class SminaEngine(BaseDockingEngine):
    """
    Smina-based docking engine implementation.

    Smina is a fork of Vina that provides better scoring functions and more features.
    This engine invokes the smina command-line tool via subprocess.
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
        Initialize the Smina docking engine.
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

    @classmethod
    def get_summary_config(cls) -> dict[str, str]:
        """
        Get the summary configuration map {display_name: internal_key}.
        """
        return {
            "minimizedAffinity": "affinity",
            "Minimized RMSD": "minimized_rmsd",
        }

    def compute_box(self, center: list[float], size: list[float]):
        """
        Define the search space (grid box).
        """
        logger.info(f"设置 Smina 搜索盒子 (中心={center}, 尺寸={size})...")
        self.box_center = center
        self.box_size = size

    def dock(self, exhaustiveness: int = 8, n_poses: int = 9, min_rmsd: float = 1.0, timeout: float = 3600):
        """
        Perform docking.
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
            "--min_rmsd_filter",  # Smina uses min_rmsd_filter not min_rmsd
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
            result = run_command(cmd_args, capture_output=True, text=True, check=True, timeout=timeout)
            logger.debug(f"Smina 输出:\n{result.stdout}")
        except CalledProcessError as e:
            logger.error(f"Smina 执行失败: {e.stderr}")
            raise RuntimeError(f"Smina 对接失败: {e.stderr}") from e
        except Exception as e:
            logger.error(f"Smina 执行异常: {e}")
            raise RuntimeError(f"Smina 对接异常: {e}") from e

    def save_results(self, output_name: str = "docked.pdbqt", output_dir: Path | None = None) -> Path:
        """
        Save docked poses.

        Actually copies the temporary output file to the target location.
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
        n_complexes: int | None = None,
        output_dir: Path | None = None,
        output_name_prefix: str = "complex_pose",
    ):
        """
        Save the docked ligand-receptor complex as a PDB file using PyMOL.
        """
        if cmd is None:
            logger.error("PyMOL 未安装。无法保存 PDB 复合物。")
            return

        target_dir = output_dir if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        if not self._temp_output_file.exists():
            logger.warning("未找到对接结果, 无法保存复合物。")
            return

        # 解析结果数量
        poses_info = self.get_all_poses_info(n_poses=999)
        total_poses = len(poses_info)

        if total_poses == 0:
            logger.warning("对接结果为空, 无法保存复合物。")
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
        Return the best energy score (kcal/mol).
        """
        if not self._temp_output_file.exists():
            return 0.0

        poses = self.get_all_poses_info(n_poses=1)
        if poses:
            return poses[0]["affinity"]
        return 0.0

    def get_all_poses_info(self, n_poses: int = 9) -> list[dict[str, Any]]:
        """
        Return information for all poses: energy, RMSD lower bound, RMSD upper bound.

        Parsed from the PDBQT output file.
        """
        if not self._temp_output_file.exists():
            return []

        results = []
        # REMARK VINA RESULT:    -8.5      0.000      0.000
        # smina 输出格式与 vina 类似
        # REMARK minimizedAffinity -4.50028801
        # REMARK minimizedRMSD -1

        vina_pattern = re.compile(r"REMARK VINA RESULT:\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")
        minimized_affinity_pattern = re.compile(r"REMARK minimizedAffinity\s+([-\d.]+)")
        minimized_rmsd_pattern = re.compile(r"REMARK minimizedRMSD\s+([-\d.]+)")

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

                    elif line.startswith("REMARK minimizedAffinity"):
                        match = minimized_affinity_pattern.search(line)
                        if match:
                            # 优先使用 minimizedAffinity
                            current_pose["affinity"] = float(match.group(1))

                    elif line.startswith("REMARK minimizedRMSD"):
                        match = minimized_rmsd_pattern.search(line)
                        if match:
                            current_pose["minimized_rmsd"] = float(match.group(1))

                    elif line.startswith("ENDMDL"):
                        if "affinity" in current_pose:
                            results.append(current_pose)
                            if len(results) >= n_poses:
                                break
                        in_model = False

        except Exception as e:
            logger.error(f"解析 Smina 结果文件失败: {e}")
            return []

        return results
