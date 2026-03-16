from __future__ import annotations

from pathlib import Path

import gemmi

from bio_analyze_core.logging import get_logger

try:
    from pymol import cmd
except ImportError:
    cmd = None

logger = get_logger(__name__)


def convert_cif_to_pdb(input_file: Path, output_file: Path | None = None) -> Path:
    """
    zh: 将 CIF/mmCIF 文件转换为 PDB 文件。
    en: Convert CIF/mmCIF file to PDB file.

    Args:
        input_file (Path):
            zh: 输入的 CIF/mmCIF 文件路径。
            en: Path to input CIF/mmCIF file.
        output_file (Optional[Path], optional):
            zh: 输出的 PDB 文件路径。如果为 None，则在同目录下生成。
            en: Path to output PDB file. If None, generated in the same directory.

    Returns:
        Path:
            zh: 生成的 PDB 文件路径。
            en: Path to generated PDB file.

    Raises:
        RuntimeError:
            zh: 如果转换失败。
            en: If conversion fails.
    """
    input_file = Path(input_file)
    output_file = input_file.parent / f"{input_file.stem}_converted.pdb" if output_file is None else Path(output_file)

    logger.info(f"Converting CIF to PDB: {input_file.name}")
    try:
        # doc = gemmi.cif.read(str(input_file))
        # block = doc.sole_block()
        # structure = gemmi.make_structure_from_block(block)
        structure = gemmi.read_structure(str(input_file))
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if structure has models/chains
        if len(structure) == 0:
            logger.warning(f"Warning: Gemmi read empty structure from {input_file}")
            
        # Write PDB string manually to avoid potential C++ file I/O issues in some environments
        pdb_string = structure.make_pdb_string()
        
        if not pdb_string:
             logger.warning(f"Warning: Gemmi generated empty PDB string for {input_file}")
             
        # Ensure pdb_string is str (especially for Mocks in tests)
        if not isinstance(pdb_string, str):
            pdb_string = str(pdb_string)

        output_file.write_text(pdb_string)
        
        if not output_file.exists():
            raise RuntimeError(f"Gemmi failed to write PDB file (file missing after write): {output_file}")
            
        logger.info(f"Converted CIF to PDB: {output_file} (size: {output_file.stat().st_size} bytes)")
        return output_file
    except Exception as e:
        logger.error(f"Failed to convert CIF to PDB: {e}")
        raise RuntimeError(f"CIF conversion failed: {e}") from e


def merge_complex_with_pymol(
    receptor_path: Path,
    ligand_poses_path: Path,
    output_dir: Path,
    n_save: int,
    output_name_prefix: str = "complex_pose",
) -> None:
    """
    zh: 使用 PyMOL 将受体和配体姿态合并为复合物 PDB 文件。
    en: Merge receptor and ligand poses into complex PDB files using PyMOL.

    Args:
        receptor_path (Path):
            zh: 受体文件路径 (PDB/PDBQT)。
            en: Path to receptor file (PDB/PDBQT).
        ligand_poses_path (Path):
            zh: 包含多个姿态的配体文件路径 (PDBQT)。
            en: Path to ligand file containing multiple poses (PDBQT).
        output_dir (Path):
            zh: 保存结果的输出目录。
            en: Output directory for saving results.
        n_save (int):
            zh: 要保存的前 N 个姿态。
            en: Number of top poses to save.
        output_name_prefix (str, optional):
            zh: 输出文件名的前缀 (默认为 "complex_pose")。
                例如前缀为 "foo"，则文件名为 "foo_1.pdb", "foo_2.pdb" 等。
            en: Prefix for output filenames (default "complex_pose").
                E.g., if prefix is "foo", filenames will be "foo_1.pdb", "foo_2.pdb", etc.
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
