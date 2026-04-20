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
    Convert CIF/mmCIF file to PDB file.

    Args:
        input_file (Path):
            Path to input CIF/mmCIF file.
        output_file (Optional[Path], optional):
            Path to output PDB file. If None, generated in the same directory.

    Returns:
        Path:
            Path to generated PDB file.

    Raises:
        RuntimeError:
            If conversion fails.
    """
    input_file = Path(input_file)
    output_file = input_file.parent / f"{input_file.stem}_converted.pdb" if output_file is None else Path(output_file)

    logger.info(f"Converting CIF to PDB: {input_file.name}")
    try:
        structure = None
        try:
            structure = gemmi.read_structure(str(input_file))
        except Exception as e:
            logger.warning(f"gemmi.read_structure failed: {e}, trying gemmi.cif.read...")

        if structure is None or len(structure) == 0:
             try:
                 doc = gemmi.cif.read(str(input_file))
                 block = doc.sole_block()
                 structure = gemmi.make_structure_from_block(block)
             except Exception as e2:
                 logger.warning(f"gemmi.cif.read failed: {e2}")
                 if structure is None:
                     raise e2

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        is_gemmi_success = False
        if structure is not None and len(structure) > 0:
            pdb_string = structure.make_pdb_string()
            if pdb_string and isinstance(pdb_string, str) and len(pdb_string) > 100:
                output_file.write_text(pdb_string)
                if output_file.exists() and output_file.stat().st_size > 100:
                    is_gemmi_success = True

        if not is_gemmi_success:
            logger.warning(f"Warning: Gemmi read empty structure or failed for {input_file}, trying PyMOL fallback...")
            if cmd is not None:
                try:
                    cmd.reinitialize()
                    cmd.load(str(input_file), "temp_cif")
                    cmd.save(str(output_file), "temp_cif")
                    cmd.delete("temp_cif")
                    if output_file.exists() and output_file.stat().st_size > 100:
                        logger.info(f"PyMOL fallback successful for {input_file}")
                        return output_file
                except Exception as e_pymol:
                    logger.warning(f"PyMOL fallback failed: {e_pymol}")

            # Try OpenBabel fallback
            logger.info(f"Trying OpenBabel fallback for {input_file}...")
            try:
                import subprocess
                subprocess.run(
                    ["obabel", "-icif", str(input_file), "-opdb", "-O", str(output_file)],
                    check=True,
                    capture_output=True,
                )
                if output_file.exists() and output_file.stat().st_size > 100:
                    logger.info(f"OpenBabel fallback successful for {input_file}")
                    return output_file
            except Exception as e_obabel:
                logger.warning(f"OpenBabel fallback failed: {e_obabel}")

            if output_file.exists():
                output_file.unlink() # remove if it's a dummy 0-byte file
            raise RuntimeError(f"All CIF to PDB conversion methods failed for {input_file}")

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
    Merge receptor and ligand poses into complex PDB files using PyMOL.

    Args:
        receptor_path (Path):
            Path to receptor file (PDB/PDBQT).
        ligand_poses_path (Path):
            Path to ligand file containing multiple poses (PDBQT).
        output_dir (Path):
            Output directory for saving results.
        n_save (int):
            Number of top poses to save.
        output_name_prefix (str, optional):
                例如前缀为 "foo"，则文件名为 "foo_1.pdb", "foo_2.pdb" 等。
            Prefix for output filenames (default "complex_pose").
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
