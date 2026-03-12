from __future__ import annotations

from pathlib import Path
from typing import Optional

import gemmi

from bio_analyze_core.logging import get_logger

try:
    from pymol import cmd
except ImportError:
    cmd = None

logger = get_logger(__name__)


def convert_cif_to_pdb(input_file: Path, output_file: Optional[Path] = None) -> Path:
    """
    将 CIF/mmCIF 文件转换为 PDB 文件。

    Args:
        input_file: 输入的 CIF/mmCIF 文件路径。
        output_file: 输出的 PDB 文件路径。如果为 None，则在同目录下生成。

    Returns:
        Path: 生成的 PDB 文件路径。

    Raises:
        RuntimeError: 如果转换失败。
    """
    input_file = Path(input_file)
    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_converted.pdb"
    else:
        output_file = Path(output_file)

    logger.info(f"Converting CIF to PDB: {input_file.name}")
    try:
        doc = gemmi.cif.read(str(input_file))
        block = doc.sole_block()
        structure = gemmi.make_structure_from_block(block)

        structure.write_pdb(str(output_file))
        logger.info(f"Converted CIF to PDB: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Failed to convert CIF to PDB: {e}")
        raise RuntimeError(f"CIF conversion failed: {e}")


def merge_complex_with_pymol(
    receptor_path: Path,
    ligand_poses_path: Path,
    output_dir: Path,
    n_save: int,
    output_name_prefix: str = "complex_pose",
) -> None:
    """
    使用 PyMOL 将受体和配体姿态合并为复合物 PDB 文件。

    Args:
        receptor_path: 受体文件路径 (PDB/PDBQT)。
        ligand_poses_path: 包含多个姿态的配体文件路径 (PDBQT)。
        output_dir: 保存结果的输出目录。
        n_save: 要保存的前 N 个姿态。
        output_name_prefix: 输出文件名的前缀 (默认为 "complex_pose")。
                            例如前缀为 "foo"，则文件名为 "foo_1.pdb", "foo_2.pdb" 等。
    """
    if cmd is None:
        logger.error("PyMOL module not found. Cannot merge complexes.")
        return

    try:
        # 重新初始化 PyMOL 以避免之前运行的干扰
        cmd.reinitialize()

        # 加载受体
        rec_obj = "receptor"
        cmd.load(str(receptor_path), rec_obj)

        # 加载配体姿态
        lig_obj = "ligand_poses"
        cmd.load(str(ligand_poses_path), lig_obj)

        # 获取加载的状态（姿态）数量
        n_states = cmd.count_states(lig_obj)

        for i in range(1, min(n_states, n_save) + 1):
            complex_name = f"complex_{i}"
            output_file = output_dir / f"{output_name_prefix}_{i}.pdb"

            # 创建一个结合受体和特定配体状态的新对象
            # 注意：ligand_poses 有多个状态。我们需要选择状态 i。
            cmd.create(complex_name, f"{rec_obj} or ({lig_obj} and state {i})")

            # 保存为 PDB
            cmd.save(str(output_file), complex_name)
            logger.debug(f"Saved complex: {output_file}")

            # 清理复合物对象
            cmd.delete(complex_name)

    except Exception as e:
        logger.error(f"Failed to generate complex PDBs with PyMOL: {e}")
    finally:
        # 清理 PyMOL 会话
        if cmd is not None:
            cmd.reinitialize()
