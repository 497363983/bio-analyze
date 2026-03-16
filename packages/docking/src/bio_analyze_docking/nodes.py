from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd

from bio_analyze_core.logging import get_logger
from bio_analyze_core.pipeline import Context, Node, Progress
from bio_analyze_core.utils import safe_save_json

from .engines import DockingEngineFactory
from .prep import get_box_from_ligand, get_box_from_receptor, prepare_ligand, prepare_receptor


def run_docking_task(
    rec_prep: str,
    lig_prep: str,
    output_dir: Path,
    rec_name: str,
    lig_name: str,
    center: list[float] | None,
    size: list[float] | None,
    exhaustiveness: int,
    n_poses: int,
    output_docked_lig_recep_struct: bool = False,
    n_docked_lig_recep_struct: int | None = None,
    engine_type: str = "vina",
    padding: float = 4.0,  # 添加 padding 参数以防自动计算
) -> dict:
    """
    zh: 并行对接执行的辅助函数。
    en: Helper function for parallel docking execution.

    Args:
        rec_prep (str):
            zh: 准备好的受体文件路径。
            en: Path to prepared receptor file.
        lig_prep (str):
            zh: 准备好的配体文件路径。
            en: Path to prepared ligand file.
        output_dir (Path):
            zh: 输出目录。
            en: Output directory.
        rec_name (str):
            zh: 受体名称。
            en: Receptor name.
        lig_name (str):
            zh: 配体名称。
            en: Ligand name.
        center (list[float] | None):
            zh: 盒子中心 [x, y, z]。如果为 None，则自动计算。
            en: Box center [x, y, z]. If None, auto-calculated.
        size (list[float] | None):
            zh: 盒子大小 [x, y, z]。如果为 None，则自动计算。
            en: Box size [x, y, z]. If None, auto-calculated.
        exhaustiveness (int):
            zh: 搜索穷尽性。
            en: Search exhaustiveness.
        n_poses (int):
            zh: 生成的姿态数量。
            en: Number of poses to generate.
        output_docked_lig_recep_struct (bool, optional):
            zh: 是否输出复合物结构。默认为 False。
            en: Whether to output complex structure. Defaults to False.
        n_docked_lig_recep_struct (int | None, optional):
            zh: 输出复合物的数量。
            en: Number of complexes to output.
        engine_type (str, optional):
            zh: 对接引擎类型。默认为 "vina"。
            en: Docking engine type. Defaults to "vina".
        padding (float, optional):
            zh: 自动盒填充。默认为 4.0。
            en: Autobox padding. Defaults to 4.0.

    Returns:
        dict:
            zh: 对接结果字典。
            en: Docking result dictionary.
    """
    output_dir = output_dir.resolve()
    # 为此任务配置记录器
    log_dir = output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    task_name = f"{Path(rec_name).stem}_{Path(lig_name).stem}"

    # 显式指定日志文件路径
    log_file = log_dir / f"{task_name}.log"

    # 使用 core 模块的 get_logger (loguru)
    logger = get_logger(f"docking_task.{task_name}", log_path=log_file, console_output=False)

    try:
        logger.info(f"开始对接任务: {rec_name} + {lig_name}")
        logger.info(f"日志文件: {log_file}")

        rec_path = Path(rec_prep)
        lig_path = Path(lig_prep)
        rec_stem = rec_path.stem
        lig_stem = lig_path.stem

        # 如果没有提供盒子参数，自动从受体计算
        if center is None:
            logger.info(f"No box center provided, calculating box from receptor: {rec_name}")
            center, size = get_box_from_receptor(rec_path, padding=padding)

        # 任务工作目录 (用于临时文件和元数据)
        # 将其移动到 dock_results/working 子目录下，避免污染主输出目录
        pair_dir = output_dir / "dock_results" / "working" / f"{rec_stem}_{lig_stem}"
        pair_dir.mkdir(parents=True, exist_ok=True)

        # 新的输出结构
        # 1. 姿态: dock_results/poses/{rec_stem}/{lig_stem}_docked{output_ext}
        engine_cls = DockingEngineFactory.get_engine_class(engine_type)
        output_ext = engine_cls.get_output_ext()
        poses_dir = output_dir / "dock_results" / "poses" / rec_stem
        poses_dir.mkdir(parents=True, exist_ok=True)
        poses_filename = f"{lig_stem}_docked{output_ext}"

        # 2. 复合物: dock_results/complex/{rec_stem}/{lig_stem}_docked_complex.pdb
        # 注意: 用户请求了 .pdbqt 后缀，但 PyMOL 默认保存 PDB。
        # 我们使用 .pdb 后缀以保持正确性，如果用户强求 .pdbqt，需要后续转换。
        complex_dir = output_dir / "dock_results" / "complex" / rec_stem
        complex_dir.mkdir(parents=True, exist_ok=True)
        complex_prefix = f"{lig_stem}_docked_complex"

        # 保存 box 参数到 JSON 文件 (任务级)
        box_params = {
            "center": center,
            "size": size,
            "exhaustiveness": exhaustiveness,
            "n_poses": n_poses,
            "engine_type": engine_type,
        }
        safe_save_json(box_params, pair_dir / "box_params.json")

        engine = DockingEngineFactory.create_engine(engine_type, rec_path, lig_path, pair_dir)
        engine.compute_box(center, size)
        engine.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)

        # 保存姿态到新路径
        out_file = engine.save_results(output_name=poses_filename, output_dir=poses_dir)

        if output_docked_lig_recep_struct:
            # save_complexes 使用 PyMOL 生成 PDB 文件
            # 保存到新路径，使用新前缀
            engine.save_complexes(
                n_complexes=n_docked_lig_recep_struct, output_dir=complex_dir, output_name_prefix=complex_prefix
            )

        best_score = engine.score()
        poses_info = engine.get_all_poses_info(n_poses=n_poses)

        logger.info(f"对接成功。最佳评分: {best_score}")

        return {
            "receptor": Path(rec_name).stem,
            "ligand": Path(lig_name).stem,
            "status": "success",
            "output_file": str(out_file),
            "best_score": best_score,
            "poses": poses_info,
            "box_center": center,
            "box_size": size,
            "engine_type": engine_type,
        }
    except Exception as e:
        logger.error(f"对接失败: {e}")
        return {"receptor": Path(rec_name).stem, "ligand": Path(lig_name).stem, "status": "failed", "error": str(e)}
    finally:
        # 确保所有日志都已写入
        from loguru import logger as loguru_logger

        try:
            loguru_logger.complete()
        except Exception:
            pass


class ReceptorPrepNode(Node):
    """
    zh: 准备受体文件的节点 (PDB -> PDBQT)。
    en: Node for preparing receptor files (PDB -> PDBQT).
    """

    def __init__(
        self,
        receptor_path: Path,
        output_dir: Path,
        context_key: str,
        ph: float = 7.4,
        keep_water: bool = False,
        rigid_macrocycles: bool = True,
        charge_model: str = "gasteiger",
        engine_type: str = "vina",
    ):
        """
        Args:
            receptor_path (Path):
                zh: 输入受体文件的路径。
                en: Path to input receptor file.
            output_dir (Path):
                zh: 保存准备后文件的目录。
                en: Directory to save prepared files.
            context_key (str):
                zh: 在上下文中存储输出路径的键。
                en: Key to store output path in context.
            ph (float, optional):
                zh: 质子化的 pH 值。默认为 7.4。
                en: pH value for protonation. Defaults to 7.4.
            keep_water (bool, optional):
                zh: 是否保留结晶水。默认为 False。
                en: Whether to keep crystal water. Defaults to False.
            rigid_macrocycles (bool, optional):
                zh: 是否将大环视为刚性。默认为 True。
                en: Whether to treat macrocycles as rigid. Defaults to True.
            charge_model (str, optional):
                zh: Meeko 的电荷模型。默认为 'gasteiger'。
                en: Charge model for Meeko. Defaults to 'gasteiger'.
            engine_type (str, optional):
                zh: 引擎类型。默认为 'vina'。
                en: Engine type. Defaults to 'vina'.
        """
        super().__init__(f"Prepare Receptor: {receptor_path.name}")
        self.receptor_path = Path(receptor_path)
        self.output_dir = Path(output_dir)
        self.context_key = context_key
        self.ph = ph
        self.keep_water = keep_water
        self.rigid_macrocycles = rigid_macrocycles
        self.charge_model = charge_model
        self.engine_type = engine_type

    def run(self, context: Context, progress: Progress, logger: Any):
        """
        zh: 执行节点逻辑。
        en: Execute node logic.

        Args:
            context (Context):
                zh: 管道上下文。
                en: Pipeline context.
            progress (Progress):
                zh: 进度报告器。
                en: Progress reporter.
            logger (Any):
                zh: 日志记录器。
                en: Logger instance.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        engine_cls = DockingEngineFactory.get_engine_class(self.engine_type)
        output_ext = engine_cls.get_receptor_ext()
        output_path = self.output_dir / f"{self.receptor_path.stem}{output_ext}"

        logger.info(f"准备受体 {self.receptor_path} 到 {output_path}")
        engine_cls.prepare_receptor(
            self.receptor_path,
            output_path,
            ph=self.ph,
            keep_water=self.keep_water,
            rigid_macrocycles=self.rigid_macrocycles,
            charge_model=self.charge_model,
        )

        # 将绝对路径存储在上下文中
        context[self.context_key] = str(output_path.resolve())


class BatchReceptorPrepNode(Node):
    """
    zh: 用于准备多个受体文件并支持断点续传的节点。
    en: Node for preparing multiple receptor files with resume support.
    """

    def __init__(
        self,
        receptors: list[Path],
        output_dir: Path,
        context_map_key: str,
        ph: float = 7.4,
        keep_water: bool = False,
        rigid_macrocycles: bool = True,
        charge_model: str = "gasteiger",
        engine_type: str = "vina",
    ):
        """
        Args:
            receptors (list[Path]):
                zh: 输入受体路径列表。
                en: List of input receptor paths.
            output_dir (Path):
                zh: 保存准备后文件的目录。
                en: Directory to save prepared files.
            context_map_key (str):
                zh: 在上下文中存储映射 {input_path_str: output_path_str} 的键。
                en: Key to store map {input_path_str: output_path_str} in context.
            ph (float, optional):
                zh: 质子化的 pH 值。默认为 7.4。
                en: pH value for protonation. Defaults to 7.4.
            keep_water (bool, optional):
                zh: 是否保留结晶水。默认为 False。
                en: Whether to keep crystal water. Defaults to False.
            rigid_macrocycles (bool, optional):
                zh: 是否将大环视为刚性。默认为 True。
                en: Whether to treat macrocycles as rigid. Defaults to True.
            charge_model (str, optional):
                zh: Meeko 的电荷模型。默认为 'gasteiger'。
                en: Charge model for Meeko. Defaults to 'gasteiger'.
            engine_type (str, optional):
                zh: 引擎类型。默认为 'vina'。
                en: Engine type. Defaults to 'vina'.
        """
        super().__init__("Batch Receptor Preparation")
        self.receptors = receptors
        self.output_dir = Path(output_dir)
        self.context_map_key = context_map_key
        self.ph = ph
        self.keep_water = keep_water
        self.rigid_macrocycles = rigid_macrocycles
        self.charge_model = charge_model
        self.engine_type = engine_type

    def run(self, context: Context, progress: Progress, logger: Any):
        """
        zh: 执行节点逻辑。
        en: Execute node logic.

        Args:
            context (Context):
                zh: 管道上下文。
                en: Pipeline context.
            progress (Progress):
                zh: 进度报告器。
                en: Progress reporter.
            logger (Any):
                zh: 日志记录器。
                en: Logger instance.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 从上下文获取现有映射或创建新的
        prep_map = context.get(self.context_map_key, {})

        # 识别剩余工作
        remaining = []
        for rec in self.receptors:
            if str(rec) not in prep_map:
                remaining.append(rec)

        if remaining:
            logger.info(f"恢复受体准备。剩余: {len(remaining)}")

            engine_cls = DockingEngineFactory.get_engine_class(self.engine_type)
            output_ext = engine_cls.get_receptor_ext()

            with ProcessPoolExecutor() as executor:
                future_to_rec = {}
                for rec in remaining:
                    output_path = self.output_dir / f"{rec.stem}{output_ext}"
                    # 将新参数传递给 prepare_receptor
                    future = executor.submit(
                        engine_cls.prepare_receptor,
                        rec,
                        output_path,
                        add_hydrogens=True,  # 默认
                        ph=self.ph,
                        keep_water=self.keep_water,
                        rigid_macrocycles=self.rigid_macrocycles,
                        charge_model=self.charge_model,
                    )
                    future_to_rec[future] = rec

                for i, future in enumerate(as_completed(future_to_rec)):
                    rec = future_to_rec[future]
                    progress.update(f"已准备受体 {rec.name} ({i+1}/{len(remaining)})")
                    try:
                        output_file = future.result()
                        prep_map[str(rec)] = str(output_file.resolve())
                    except Exception as e:
                        logger.error(f"准备受体 {rec} 失败: {e}")

            context[self.context_map_key] = prep_map
            context.checkpoint()
        else:
            logger.info("所有受体已准备完毕。")


class LigandPrepNode(Node):
    """
    zh: 准备配体文件的节点 (SDF/MOL2/PDB -> PDBQT)。
    en: Node for preparing ligand files (SDF/MOL2/PDB -> PDBQT).
    """

    def __init__(self, ligand_path: Path, output_dir: Path, context_key: str, engine_type: str = "vina"):
        """
        Args:
            ligand_path (Path):
                zh: 输入配体文件的路径。
                en: Path to input ligand file.
            output_dir (Path):
                zh: 保存准备后文件的目录。
                en: Directory to save prepared files.
            context_key (str):
                zh: 在上下文中存储输出路径的键。
                en: Key to store output path in context.
            engine_type (str, optional):
                zh: 引擎类型。默认为 'vina'。
                en: Engine type. Defaults to 'vina'.
        """
        super().__init__(f"Prepare Ligand: {ligand_path.name}")
        self.ligand_path = Path(ligand_path)
        self.output_dir = Path(output_dir)
        self.context_key = context_key
        self.engine_type = engine_type

    def run(self, context: Context, progress: Progress, logger: Any):
        """
        zh: 执行节点逻辑。
        en: Execute node logic.

        Args:
            context (Context):
                zh: 管道上下文。
                en: Pipeline context.
            progress (Progress):
                zh: 进度报告器。
                en: Progress reporter.
            logger (Any):
                zh: 日志记录器。
                en: Logger instance.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        engine_cls = DockingEngineFactory.get_engine_class(self.engine_type)
        output_ext = engine_cls.get_ligand_ext()
        output_path = self.output_dir / f"{self.ligand_path.stem}{output_ext}"

        logger.info(f"准备配体 {self.ligand_path} 到 {output_path}")
        engine_cls.prepare_ligand(self.ligand_path, output_path)

        # 将绝对路径存储在上下文中
        context[self.context_key] = str(output_path.resolve())


class BatchLigandPrepNode(Node):
    """
    zh: 用于准备多个配体文件并支持断点续传的节点。
    en: Node for preparing multiple ligand files with resume support.
    """

    def __init__(self, ligands: list[Path], output_dir: Path, context_map_key: str, engine_type: str = "vina"):
        """
        Args:
            ligands (list[Path]):
                zh: 输入配体路径列表。
                en: List of input ligand paths.
            output_dir (Path):
                zh: 保存准备后文件的目录。
                en: Directory to save prepared files.
            context_map_key (str):
                zh: 在上下文中存储映射 {input_path_str: output_path_str} 的键。
                en: Key to store map {input_path_str: output_path_str} in context.
            engine_type (str, optional):
                zh: 引擎类型。默认为 'vina'。
                en: Engine type. Defaults to 'vina'.
        """
        super().__init__("Batch Ligand Preparation")
        self.ligands = ligands
        self.output_dir = Path(output_dir)
        self.context_map_key = context_map_key
        self.engine_type = engine_type

    def run(self, context: Context, progress: Progress, logger: Any):
        """
        zh: 执行节点逻辑。
        en: Execute node logic.

        Args:
            context (Context):
                zh: 管道上下文。
                en: Pipeline context.
            progress (Progress):
                zh: 进度报告器。
                en: Progress reporter.
            logger (Any):
                zh: 日志记录器。
                en: Logger instance.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 从上下文获取现有映射或创建新的
        prep_map = context.get(self.context_map_key, {})

        # 识别剩余工作
        remaining = []
        for lig in self.ligands:
            if str(lig) not in prep_map:
                remaining.append(lig)

        if remaining:
            logger.info(f"恢复配体准备。剩余: {len(remaining)}")

            engine_cls = DockingEngineFactory.get_engine_class(self.engine_type)
            output_ext = engine_cls.get_ligand_ext()

            with ProcessPoolExecutor() as executor:
                future_to_lig = {}
                for lig in remaining:
                    output_path = self.output_dir / f"{lig.stem}{output_ext}"
                    future = executor.submit(engine_cls.prepare_ligand, lig, output_path)
                    future_to_lig[future] = lig

                for i, future in enumerate(as_completed(future_to_lig)):
                    lig = future_to_lig[future]
                    progress.update(f"已准备配体 {lig.name} ({i+1}/{len(remaining)})")
                    try:
                        output_file = future.result()
                        prep_map[str(lig)] = str(output_file.resolve())
                    except Exception as e:
                        logger.error(f"准备配体 {lig} 失败: {e}")

            context[self.context_map_key] = prep_map
            context.checkpoint()
        else:
            logger.info("所有配体已准备完毕。")


class DockingNode(Node):
    """
    使用准备好的文件执行对接的节点。
    """

    def __init__(
        self,
        receptor_key: str,
        ligand_key: str,
        output_dir: Path,
        center: list[float] | None = None,
        size: list[float] = [20.0, 20.0, 20.0],
        autobox_ligand: Path | None = None,
        padding: float = 4.0,
        exhaustiveness: int = 8,
        n_poses: int = 9,
        result_key: str = "docking_results",
        output_docked_lig_recep_struct: bool = False,
        n_docked_lig_recep_struct: int | None = None,
        engine_type: str = "vina",
    ):
        """
        Args:
            receptor_key: 准备好的受体路径的上下文键。
            ligand_key: 准备好的配体路径的上下文键。
            output_dir: 保存对接结果的目录。
            center: 盒子中心 [x, y, z]。
            size: 盒子大小 [x, y, z]。
            autobox_ligand: 用于自动盒计算的配体路径。
            padding: 自动盒的填充。
            exhaustiveness: 搜索详尽程度。
            n_poses: 生成的姿态数量。
            result_key: 存储结果字典的上下文键。
            output_docked_lig_recep_struct: 是否保存复合物结构（PDB 格式，通过 PyMOL）。
            n_docked_lig_recep_struct: 要保存的前几名复合物数量（None=全部）。
            engine_type: 对接引擎类型 (默认: "vina")。
        """
        super().__init__("Single Docking")
        self.receptor_key = receptor_key
        self.ligand_key = ligand_key
        self.output_dir = Path(output_dir)
        self.center = center
        self.size = size
        self.autobox_ligand = autobox_ligand
        self.padding = padding
        self.exhaustiveness = exhaustiveness
        self.n_poses = n_poses
        self.result_key = result_key
        self.output_docked_lig_recep_struct = output_docked_lig_recep_struct
        self.n_docked_lig_recep_struct = n_docked_lig_recep_struct
        self.engine_type = engine_type

    def run(self, context: Context, progress: Progress, logger: Any):
        rec_prep = context.get(self.receptor_key)
        lig_prep = context.get(self.ligand_key)

        if not rec_prep or not lig_prep:
            raise RuntimeError("在上下文中未找到准备好的受体或配体。")

        rec_path = Path(rec_prep)
        lig_path = Path(lig_prep)

        # 确定盒子
        center = self.center
        size = self.size

        if self.autobox_ligand:
            center, size = get_box_from_ligand(self.autobox_ligand, padding=self.padding)
        elif center is None:
            # 如果未提供 center，则根据受体自动计算盒子
            logger.info(f"No box center provided, calculating box from receptor: {rec_path.name}")
            center, size = get_box_from_receptor(rec_path, padding=self.padding)

        logger.info(f"正在对接 {rec_path.name} 和 {lig_path.name}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        try:
            engine = DockingEngineFactory.create_engine(self.engine_type, rec_path, lig_path, self.output_dir)
            engine.compute_box(center, size)
            engine.dock(exhaustiveness=self.exhaustiveness, n_poses=self.n_poses)

            engine_cls = DockingEngineFactory.get_engine_class(self.engine_type)
            output_ext = engine_cls.get_output_ext()
            out_file = engine.save_results(output_name=f"docked{output_ext}")

            if self.output_docked_lig_recep_struct:
                engine.save_complexes(self.n_docked_lig_recep_struct)

            best_score = engine.score()
            poses_info = engine.get_all_poses_info(n_poses=self.n_poses)

            result = {
                "receptor": rec_path.name,
                "ligand": lig_path.name,
                "status": "success",
                "output_file": str(out_file),
                "best_score": best_score,
                "poses": poses_info,
                "box_center": center,
                "box_size": size,
                "engine_type": self.engine_type,
            }
        except Exception as e:
            logger.error(f"对接失败 {self.receptor_key} + {self.ligand_key}: {e}")
            result = {
                "receptor": rec_path.name if rec_path else self.receptor_key,
                "ligand": lig_path.name if lig_path else self.ligand_key,
                "status": "failed",
                "error": str(e),
            }

        # 将结果追加到上下文
        # 我们需要处理并发访问（如果我们是并行的），但目前 Pipeline 是顺序的。
        # 但是，我们需要确保读取当前列表并追加到它。
        current_results = context.get(self.result_key, [])
        if not isinstance(current_results, list):
            current_results = []
        current_results.append(result)
        context[self.result_key] = current_results


class BatchDockingNode(Node):
    """
    执行 M x N 对接并支持断点续传的节点。
    """

    def __init__(
        self,
        receptors: list[Path],
        ligands: list[Path],
        output_dir: Path,
        context_key_receptors: str,
        context_key_ligands: str,
        center: list[float] | None = None,
        size: list[float] = [20.0, 20.0, 20.0],
        autobox_ligand: Path | None = None,
        padding: float = 4.0,
        exhaustiveness: int = 8,
        n_poses: int = 9,
        result_key: str = "docking_results",
        output_docked_lig_recep_struct: bool = False,
        n_docked_lig_recep_struct: int | None = None,
        engine_type: str = "vina",
    ):
        """
        Args:
            receptors: 输入受体列表。
            ligands: 输入配体列表。
            output_dir: 保存结果的目录。
            context_key_receptors: 受体准备映射的键。
            context_key_ligands: 配体准备映射的键。
            center: 盒子中心。
            size: 盒子大小。
            autobox_ligand: 自动盒路径。
            padding: 填充。
            exhaustiveness: 搜索详尽程度。
            n_poses: 姿态数量。
            result_key: 结果的上下文键。
            output_docked_lig_recep_struct: 是否保存复合物结构。
            n_docked_lig_recep_struct: 要保存的前几名复合物数量（None=全部）。
            engine_type: 对接引擎类型 (默认: "vina")。
        """
        super().__init__("Batch Docking")
        self.receptors = receptors
        self.ligands = ligands
        self.output_dir = Path(output_dir)
        self.context_key_receptors = context_key_receptors
        self.context_key_ligands = context_key_ligands
        self.center = center
        self.size = size
        self.autobox_ligand = autobox_ligand
        self.padding = padding
        self.exhaustiveness = exhaustiveness
        self.n_poses = n_poses
        self.result_key = result_key
        self.output_docked_lig_recep_struct = output_docked_lig_recep_struct
        self.n_docked_lig_recep_struct = n_docked_lig_recep_struct
        self.engine_type = engine_type

    def run(self, context: Context, progress: Progress, logger: Any):
        rec_map = context.get(self.context_key_receptors, {})
        lig_map = context.get(self.context_key_ligands, {})

        # 我们迭代 __init__ 中提供的 *原始* 输入列表
        # 但我们需要在映射中查找准备好的路径。

        completed_keys = set(context.get("docking_completed_keys", []))
        results = context.get(self.result_key, [])
        if not isinstance(results, list):
            results = []

        total_tasks = len(self.receptors) * len(self.ligands)
        completed_count = len(completed_keys)
        logger.info(f"开始批量对接。总计: {total_tasks}, 已完成: {completed_count}")

        # 准备任务
        tasks = []
        for rec in self.receptors:
            for lig in self.ligands:
                key = f"{rec.name}::{lig.name}"
                if key in completed_keys:
                    continue

                rec_prep = rec_map.get(str(rec))
                lig_prep = lig_map.get(str(lig))

                if not rec_prep or not lig_prep:
                    logger.warning(f"跳过 {key}: 准备失败或丢失。")
                    # 添加失败的结果条目以便出现在摘要中
                    results.append(
                        {
                            "receptor": rec.stem,
                            "ligand": lig.stem,
                            "status": "failed",
                            "error": "Preparation failed or file missing",
                        }
                    )
                    completed_keys.add(key)
                    continue

                tasks.append((key, rec, lig, rec_prep, lig_prep))

        if not tasks:
            logger.info("没有剩余的对接任务。")
            return

        # 如果需要，预计算盒子
        center = self.center
        size = self.size

        # 如果使用 autobox_ligand，我们不能在这里计算全局 center/size，
        # 因为它取决于具体的配体（如果 autobox_ligand 是针对每个任务的，但这里传入的是单个路径...）
        # 等等，BatchDockingNode 接收的是 self.autobox_ligand (单个路径)。
        # 这意味着目前所有任务都使用同一个 autobox 配体？这似乎不太合理，除非该配体是共结晶配体。
        # 如果 autobox_ligand 为空，则必须提供 center。

        # 修正逻辑：
        # 我们不再在这里保存全局唯一的 configs.json，而是收集所有任务的配置。
        # 但是任务是并发运行的。我们可以先初始化一个空的 configs 字典，或者在收集结果时构建它。
        # 更好的方法是在 run_docking_task 返回结果中包含 box 信息（已经包含了），
        # 然后在所有任务完成后，根据 results 生成 configs.json。

        if self.autobox_ligand:
            center, size = get_box_from_ligand(self.autobox_ligand, padding=self.padding)
        elif center is None:
            # 如果未提供 center，则在 run_docking_task 中根据每个受体单独计算
            pass

        # 不再在任务开始前保存单条目的 configs.json
        # safe_save_json(configs, self.output_dir / "configs.json")

        # 我们将在收集结果后保存完整的 configs.json

        with ProcessPoolExecutor() as executor:
            future_to_key = {}
            for key, rec, lig, rec_prep, lig_prep in tasks:
                # 如果 center 是 None，run_docking_task 需要知道如何处理
                future = executor.submit(
                    run_docking_task,
                    rec_prep,
                    lig_prep,
                    self.output_dir,
                    rec.name,
                    lig.name,
                    center,  # 可能为 None
                    size,  # 可能为 None
                    self.exhaustiveness,
                    self.n_poses,
                    self.output_docked_lig_recep_struct,
                    self.n_docked_lig_recep_struct,
                    self.engine_type,
                    self.padding,  # 传递 padding
                )
                future_to_key[future] = key

            for i, future in enumerate(as_completed(future_to_key)):
                key = future_to_key[future]
                completed_count += 1
                progress.update(f"对接完成 ({completed_count}/{total_tasks})")

                try:
                    result = future.result()
                    results.append(result)
                    completed_keys.add(key)

                    # 每 5 个任务检查点一次
                    if len(results) % 5 == 0:
                        context[self.result_key] = results
                        context["docking_completed_keys"] = list(completed_keys)
                        context.checkpoint()

                except Exception as e:
                    logger.error(f"对接任务 {key} 失败: {e}")

        # 最终检查点
        context[self.result_key] = results
        context["docking_completed_keys"] = list(completed_keys)
        context.checkpoint()

        # 生成并保存包含受体配置的 configs.json
        # 即使对同一个受体进行了多次对接（针对不同配体），盒子参数通常是针对受体的。
        # 如果盒子是基于配体自动计算的 (autobox_ligand)，那么它可能随配体变化。
        # 但用户的需求似乎是“针对每个受体有对应的box_center和box_size”，暗示受体是主键。

        final_configs = {}
        for res in results:
            if res.get("status") == "success":
                rec = res.get("receptor")
                # 我们只记录每个受体一次。
                # 如果盒子参数随配体变化，这里只会记录最后一次成功对接的参数。
                # 考虑到用户需求是“只要受体即可”，这应该是可以接受的。

                if rec not in final_configs:
                    final_configs[rec] = {
                        "box_center": res.get("box_center"),
                        "box_size": res.get("box_size"),
                        "exhaustiveness": self.exhaustiveness,
                        "n_poses": self.n_poses,
                        "engine_type": self.engine_type,
                    }

        safe_save_json(final_configs, self.output_dir / "configs.json")
        logger.info(f"已保存受体配置到: {self.output_dir / 'configs.json'}")


class ResultSummaryNode(Node):
    """
    将对接结果汇总到文件 (CSV/Excel/TSV) 的节点。
    """

    def __init__(self, input_key: str, output_path: Path, format: str = "csv"):
        """
        Args:
            input_key: 包含对接结果字典列表的上下文键。
            output_path: 保存摘要文件的路径。
            format: 输出格式 ('csv', 'excel', 'tsv')。
        """
        super().__init__("Generate Docking Summary")
        self.input_key = input_key
        self.output_path = Path(output_path)
        self.format = format.lower()

    def run(self, context: Context, progress: Progress, logger: Any):
        results = context.get(self.input_key, [])
        if not results:
            logger.warning("未找到可汇总的对接结果。")
            return

        # 扁平化 DataFrame 的结果
        data = []
        for res in results:
            if res.get("status") != "success":
                data.append(
                    {
                        "Receptor": res.get("receptor"),
                        "Ligand": res.get("ligand"),
                        "Status": res.get("status"),
                        "Error": res.get("error"),
                        "Affinity (kcal/mol)": None,
                        "RMSD l.b.": None,
                        "RMSD u.b.": None,
                        "Box Center X": None,
                        "Box Center Y": None,
                        "Box Center Z": None,
                        "Box Size X": None,
                        "Box Size Y": None,
                        "Box Size Z": None,
                        "Output File": None,
                    }
                )
                continue

            # 获取最佳姿态（姿态 1）
            poses = res.get("poses", [])
            best_pose = poses[0] if poses else {}

            # 获取 Box 信息
            center = res.get("box_center", [None, None, None])
            size = res.get("box_size", [None, None, None])

            data.append(
                {
                    "Receptor": res.get("receptor"),
                    "Ligand": res.get("ligand"),
                    "Status": "Success",
                    "Error": None,
                    "Affinity (kcal/mol)": best_pose.get("affinity"),
                    "RMSD l.b.": best_pose.get("rmsd_lb"),
                    "RMSD u.b.": best_pose.get("rmsd_ub"),
                    "Box Center X": center[0],
                    "Box Center Y": center[1],
                    "Box Center Z": center[2],
                    "Box Size X": size[0],
                    "Box Size Y": size[1],
                    "Box Size Z": size[2],
                    "Output File": res.get("output_file"),
                }
            )

        if not data:
            logger.warning("没有提取到用于汇总的数据。")
            return

        df = pd.DataFrame(data)

        # 确保列顺序，如果需要的话
        desired_columns = [
            "Receptor",
            "Ligand",
            "Status",
            "Error",
            "Affinity (kcal/mol)",
            "RMSD l.b.",
            "RMSD u.b.",
            "Box Center X",
            "Box Center Y",
            "Box Center Z",
            "Box Size X",
            "Box Size Y",
            "Box Size Z",
            "Output File",
        ]

        # 仅选择存在的列（防止 data 为空时导致的问题，尽管我们已经检查过 data）
        # 如果 df 是空的，to_csv 会写一个空文件或只有标题

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"正在将汇总写入 {self.output_path} (格式: {self.format})")

        if self.format == "csv":
            df.to_csv(self.output_path, index=False, columns=desired_columns)
        elif self.format == "tsv":
            df.to_csv(self.output_path, sep="\t", index=False, columns=desired_columns)
        elif self.format in ["excel", "xlsx"]:
            df.to_excel(self.output_path, index=False, columns=desired_columns)
        else:
            raise ValueError(f"不支持的格式: {self.format}")
