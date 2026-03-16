from __future__ import annotations

from pathlib import Path

from bio_analyze_core.pipeline import Pipeline

from .engine import DockingEngine
from .nodes import (
    BatchDockingNode,
    BatchLigandPrepNode,
    BatchReceptorPrepNode,
    DockingNode,
    LigandPrepNode,
    ReceptorPrepNode,
    ResultSummaryNode,
)
from .prep import get_box_from_ligand, prepare_ligand, prepare_receptor

__all__ = [
    "prepare_ligand",
    "prepare_receptor",
    "get_box_from_ligand",
    "DockingEngine",
    "run_docking",
    "run_docking_batch",
]


def run_docking(
    receptor: Path,
    ligand: Path,
    output_dir: Path,
    center: list[float] | None = None,
    size: list[float] = [20.0, 20.0, 20.0],
    autobox_ligand: Path | None = None,
    padding: float = 4.0,
    exhaustiveness: int = 8,
    n_poses: int = 9,
    summary_filename: str | None = "docking_summary.csv",
    output_docked_lig_recep_struct: bool = False,
    n_docked_lig_recep_struct: int | None = None,
    charge_model: str = "gasteiger",
    engine: str = "vina",
) -> dict:
    """
    zh: 运行单个受体-配体对的完整对接流程。
    en: Run complete docking pipeline for a single receptor-ligand pair.

    Args:
        receptor:
            zh: 受体文件路径 (PDB/PDBQT)。
            en: Path to receptor file (PDB/PDBQT).
        ligand:
            zh: 配体文件路径 (SDF/MOL2/PDB/SMILES)。
            en: Path to ligand file (SDF/MOL2/PDB/SMILES).
        output_dir:
            zh: 输出目录。
            en: Output directory.
        center:
            zh: 盒子中心 [x, y, z]。
            en: Box center [x, y, z].
        size:
            zh: 盒子大小 [x, y, z]。
            en: Box size [x, y, z].
        autobox_ligand:
            zh: 用于自动盒计算的配体路径。
            en: Ligand path for autobox calculation.
        padding:
            zh: 自动盒填充。
            en: Autobox padding.
        exhaustiveness:
            zh: Vina 穷尽性。
            en: Vina exhaustiveness.
        n_poses:
            zh: 姿态数量。
            en: Number of poses.
        summary_filename:
            zh: 摘要文件名。
            en: Summary filename.
        output_docked_lig_recep_struct:
            zh: 是否保存复合物结构（PDB 格式，通过 PyMOL）。
            en: Whether to save complex structure (PDB format, via PyMOL).
        n_docked_lig_recep_struct:
            zh: 要保存的复合物数量。
            en: Number of complexes to save.
        charge_model:
            zh: 受体准备的电荷模型 (例如 'gasteiger', 'zero')。
            en: Charge model for receptor preparation (e.g. 'gasteiger', 'zero').
        engine:
            zh: 对接引擎类型 (例如 'vina', 'gnina')。
            en: Docking engine type (e.g. 'vina', 'gnina').
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建流程
    pipeline = Pipeline("single_docking", str(output_dir / "pipeline_state.json"))

    # 定义键
    rec_key = "receptor_prepared"
    lig_key = "ligand_prepared"
    result_key = "docking_results"

    # 添加节点
    pipeline.add_node(ReceptorPrepNode(receptor, output_dir, rec_key, charge_model=charge_model, engine_type=engine))
    pipeline.add_node(LigandPrepNode(ligand, output_dir, lig_key, engine_type=engine))

    pipeline.add_node(
        DockingNode(
            receptor_key=rec_key,
            ligand_key=lig_key,
            output_dir=output_dir,
            center=center,
            size=size,
            autobox_ligand=autobox_ligand,
            padding=padding,
            exhaustiveness=exhaustiveness,
            n_poses=n_poses,
            result_key=result_key,
            output_docked_lig_recep_struct=output_docked_lig_recep_struct,
            n_docked_lig_recep_struct=n_docked_lig_recep_struct,
            engine_type=engine,
        )
    )

    # 如果需要，添加摘要节点
    if summary_filename:
        # 从扩展名确定格式
        ext = Path(summary_filename).suffix.lower()
        if ext in [".csv"]:
            fmt = "csv"
        elif ext in [".tsv"]:
            fmt = "tsv"
        elif ext in [".xlsx", ".xls"]:
            fmt = "excel"
        else:
            fmt = "csv"  # 默认回退

        pipeline.add_node(
            ResultSummaryNode(input_key=result_key, output_path=output_dir / summary_filename, format=fmt)
        )

    # 运行流程
    pipeline.run()

    # 获取结果
    results = pipeline.context.get(result_key, [])
    if results:
        return results[-1]
    else:
        # 如果 DockingNode 成功运行（或捕获异常），这不应该发生
        raise RuntimeError("Docking pipeline finished but no result found.")


def run_docking_batch(
    receptors: list[Path] | Path,
    ligands: list[Path] | Path,
    output_dir: Path,
    center: list[float] | None = None,
    size: list[float] = [20.0, 20.0, 20.0],
    autobox_ligand: Path | None = None,
    padding: float = 4.0,
    exhaustiveness: int = 8,
    n_poses: int = 9,
    summary_filename: str | None = "docking_summary.csv",
    output_docked_lig_recep_struct: bool = False,
    n_docked_lig_recep_struct: int | None = None,
    charge_model: str = "gasteiger",
    engine: str = "vina",
) -> list[dict]:
    """
    zh: 对多个受体和/或配体 (M x N) 运行对接。
    en: Run docking for multiple receptors and/or ligands (M x N).

    Args:
        receptors:
            zh: 受体路径列表或包含受体的目录。
            en: List of receptor paths or directory containing receptors.
        ligands:
            zh: 配体路径列表或包含配体的目录。
            en: List of ligand paths or directory containing ligands.
        output_dir:
            zh: 基础输出目录。
            en: Base output directory.
        center:
            zh: 盒子中心 [x, y, z]。
            en: Box center [x, y, z].
        size:
            zh: 盒子大小 [x, y, z]。
            en: Box size [x, y, z].
        autobox_ligand:
            zh: 用于自动盒计算的配体路径。
            en: Ligand path for autobox calculation.
        padding:
            zh: 自动盒填充。
            en: Autobox padding.
        exhaustiveness:
            zh: Vina 穷尽性。
            en: Vina exhaustiveness.
        n_poses:
            zh: 姿态数量。
            en: Number of poses.
        summary_filename:
            zh: 摘要文件名（例如 'summary.csv', 'results.xlsx'）或 None 以禁用。
            en: Summary filename (e.g. 'summary.csv', 'results.xlsx') or None to disable.
        output_docked_lig_recep_struct:
            zh: 是否输出对接的复合物结构（PDB 格式，通过 PyMOL）。
            en: Whether to output docked complex structures (PDB format, via PyMOL).
        n_docked_lig_recep_struct:
            zh: 要保存的前几名复合物数量（None=全部）。
            en: Number of top complexes to save (None=All).
        charge_model:
            zh: 受体准备的电荷模型 (例如 'gasteiger', 'zero')。
            en: Charge model for receptor preparation (e.g. 'gasteiger', 'zero').
        engine:
            zh: 对接引擎类型 (例如 'vina', 'gnina')。
            en: Docking engine type (e.g. 'vina', 'gnina').
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 解析输入
    if isinstance(receptors, (str, Path)):
        receptors = Path(receptors)
        if receptors.is_dir():
            receptors = (
                list(receptors.glob("*.pdb"))
                + list(receptors.glob("*.pdbqt"))
                + list(receptors.glob("*.cif"))
                + list(receptors.glob("*.mmcif"))
            )
        else:
            receptors = [receptors]

    if isinstance(ligands, (str, Path)):
        ligands = Path(ligands)
        if ligands.is_dir():
            ligands = (
                list(ligands.glob("*.sdf"))
                + list(ligands.glob("*.pdb"))
                + list(ligands.glob("*.mol2"))
                + list(ligands.glob("*.smi"))
            )
        else:
            ligands = [ligands]

    # 创建流程
    pipeline = Pipeline("batch_docking", str(output_dir / "pipeline_state.json"))

    # 识别唯一输入并分配上下文键
    unique_receptors = sorted(list(set(receptors)))
    unique_ligands = sorted(list(set(ligands)))

    rec_map_key = "receptor_prep_map"
    lig_map_key = "ligand_prep_map"
    result_key = "docking_results"

    # 添加批量准备节点
    pipeline.add_node(
        BatchReceptorPrepNode(
            receptors=unique_receptors,
            output_dir=output_dir / "prepared_receptors",
            context_map_key=rec_map_key,
            charge_model=charge_model,
            engine_type=engine,
        )
    )

    pipeline.add_node(
        BatchLigandPrepNode(
            ligands=unique_ligands, output_dir=output_dir / "prepared_ligands", context_map_key=lig_map_key, engine_type=engine
        )
    )

    # 添加批量对接节点
    pipeline.add_node(
        BatchDockingNode(
            receptors=receptors,
            ligands=ligands,
            output_dir=output_dir,
            context_key_receptors=rec_map_key,
            context_key_ligands=lig_map_key,
            center=center,
            size=size,
            autobox_ligand=autobox_ligand,
            padding=padding,
            exhaustiveness=exhaustiveness,
            n_poses=n_poses,
            result_key=result_key,
            output_docked_lig_recep_struct=output_docked_lig_recep_struct,
            n_docked_lig_recep_struct=n_docked_lig_recep_struct,
            engine_type=engine,
        )
    )

    # 如果需要，添加摘要节点
    if summary_filename:
        # 从扩展名确定格式
        ext = Path(summary_filename).suffix.lower()
        if ext in [".csv"]:
            fmt = "csv"
        elif ext in [".tsv"]:
            fmt = "tsv"
        elif ext in [".xlsx", ".xls"]:
            fmt = "excel"
        else:
            fmt = "csv"  # 默认回退

        pipeline.add_node(
            ResultSummaryNode(input_key=result_key, output_path=output_dir / summary_filename, format=fmt)
        )

    # 运行流程
    pipeline.run()

    return pipeline.context.get(result_key, [])
