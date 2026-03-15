from __future__ import annotations

import shutil
import sys
from pathlib import Path

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import CalledProcessError
from bio_analyze_core.subprocess import run as run_command

try:
    from openbabel import openbabel
except ImportError:
    openbabel = None

from meeko import MoleculePreparation

try:
    from propka.lib import loadOptions
    from propka.molecular_container import MolecularContainer
    from propka.parameters import Parameters
except ImportError:
    pass
import numpy as np
from openmm.app import PDBFile
from pdbfixer import PDBFixer
from rdkit import Chem
from rdkit.Chem import AllChem

from .utils import convert_cif_to_pdb

logger = get_logger(__name__)


def prepare_ligand(input_file: Path, output_file: Path, add_hydrogens: bool = True) -> Path:
    """
    zh: 准备配体用于对接 (SDF/SMILES -> PDBQT)。
    en: Prepare ligand for docking (SDF/SMILES -> PDBQT).

    使用 RDKit 生成 3D 结构，使用 Meeko 转换为 PDBQT 格式。
    Uses RDKit to generate 3D structure, and Meeko to convert to PDBQT format.

    Args:
        input_file (Path):
            zh: 输入配体文件路径 (SDF, MOL2, PDB, SMI)。
            en: Path to input ligand file (SDF, MOL2, PDB, SMI).
        output_file (Path):
            zh: 输出 PDBQT 文件路径。
            en: Path to output PDBQT file.
        add_hydrogens (bool, optional):
            zh: 是否自动添加氢原子并生成 3D 构象。默认为 True。
            en: Whether to automatically add hydrogens and generate 3D conformation. Defaults to True.

    Returns:
        Path:
            zh: 生成的 PDBQT 文件路径。
            en: Path to generated PDBQT file.
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    # 1. 读取分子
    mol = None
    ext = input_file.suffix.lower()

    if ext == ".sdf":
        suppl = Chem.SDMolSupplier(str(input_file))
        mol = next(suppl) if len(suppl) > 0 else None
    elif ext == ".smi" or ext == ".smiles":
        with open(input_file) as f:
            smiles = f.read().strip()
        mol = Chem.MolFromSmiles(smiles)
    elif ext == ".pdb":
        mol = Chem.MolFromPDBFile(str(input_file))
    elif ext == ".mol2":
        mol = Chem.MolFromMol2File(str(input_file))

    if mol is None:
        raise ValueError(f"Could not read ligand from {input_file}")

    # 2. 加氢并生成 3D 坐标
    if add_hydrogens:
        mol = Chem.AddHs(mol, addCoords=True)

    # 如果缺失 3D 构象，则生成
    if mol.GetNumConformers() == 0:
        logger.info(f"Generating 3D coordinates for ligand {input_file.name}...")
        AllChem.EmbedMolecule(mol, randomSeed=42)
        try:
            AllChem.MMFFOptimizeMolecule(mol)
        except ValueError:
            pass  # 某些分子可能无法进行 MMFF 优化

    # 3. 使用 Meeko 转换为 PDBQT
    logger.info(f"Converting ligand to PDBQT: {output_file.name}")
    preparator = MoleculePreparation()
    preparator.prepare(mol)
    pdbqt_string = preparator.write_pdbqt_string()

    with open(output_file, "w") as f:
        f.write(pdbqt_string)

    return output_file


def prepare_receptor(
    input_file: Path,
    output_file: Path,
    add_hydrogens: bool = True,
    ph: float = 7.4,
    keep_water: bool = False,
    rigid_macrocycles: bool = True,
    charge_model: str = "gasteiger",
) -> Path:
    """
    zh: 准备受体用于对接 (PDB -> PDBQT)。
    en: Prepare receptor for docking (PDB -> PDBQT).

    使用 PDBFixer 修复结构，PropKa 进行 pKa 分析，并使用 Meeko 转换为 PDBQT 格式。
    Uses PDBFixer to repair structure, PropKa for pKa analysis, and Meeko to convert to PDBQT format.

    Args:
        input_file (Path):
            zh: 输入 PDB 文件路径。
            en: Path to input PDB file.
        output_file (Path):
            zh: 输出 PDBQT 文件路径。
            en: Path to output PDBQT file.
        add_hydrogens (bool, optional):
            zh: 是否加氢。默认为 True。
            en: Whether to add hydrogens. Defaults to True.
        ph (float, optional):
            zh: 质子化状态计算的 pH 值。默认为 7.4。
            en: pH value for protonation state calculation. Defaults to 7.4.
        keep_water (bool, optional):
            zh: 是否保留结晶水。默认为 False。
            en: Whether to keep crystal water. Defaults to False.
        rigid_macrocycles (bool, optional):
            zh: 是否将大环视为刚性。默认为 True。
            en: Whether to treat macrocycles as rigid. Defaults to True.
        charge_model (str, optional):
            zh: Meeko 的电荷模型 (例如 'gasteiger', 'zero', 'scikit_learn')。默认为 'gasteiger'。
            en: Charge model for Meeko (e.g. 'gasteiger', 'zero', 'scikit_learn'). Defaults to 'gasteiger'.

    Returns:
        Path:
            zh: 生成的 PDBQT 文件路径。
            en: Path to generated PDBQT file.
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    # 检查输入是否已经是 PDBQT
    if input_file.suffix.lower() == ".pdbqt":
        logger.info("Input is already PDBQT, copying to output.")
        shutil.copy(input_file, output_file)
        return output_file

    # 处理 CIF/mmCIF 输入，先转换为 PDB
    processing_file = input_file
    if input_file.suffix.lower() in [".cif", ".mmcif"]:
        try:
            temp_pdb = output_file.parent / f"{input_file.stem}_converted.pdb"
            processing_file = convert_cif_to_pdb(input_file, temp_pdb)
        except Exception as e:
            # logger.error 已经在 convert_cif_to_pdb 中记录
            raise RuntimeError(f"CIF conversion failed: {e}")

    # 1. 使用 PDBFixer 修复 PDB 结构
    logger.info(f"Repairing PDB structure using PDBFixer: {processing_file.name}")
    try:
        fixer = PDBFixer(filename=str(processing_file))
        fixer.findMissingResidues()
        fixer.findNonstandardResidues()
        fixer.replaceNonstandardResidues()
        # 注意：PDBFixer 的 removeHeterogens 方法比较粗暴，我们在这一步先保留所有
        # PropKa/Meeko 阶段再决定是否去水

        fixer.findMissingAtoms()
        if fixer.missingAtoms:
            fixer.addMissingAtoms()

        # PDBFixer 会根据 pH 自动加氢，但 PropKa 会覆盖这些氢
        # 参考：PDBFixer 会在这一步自动加氢！但我们随后会用 PropKa 覆盖这些氢。
        fixer.addMissingHydrogens(pH=ph)

        # 将修复后的 PDB 保存到临时文件
        fixed_pdb_path = output_file.parent / f"{input_file.stem}_fixed.pdb"
        with open(fixed_pdb_path, "w") as f:
            PDBFile.writeFile(fixer.topology, fixer.positions, f, keepIds=True)

        logger.info(f"Fixed PDB saved to: {fixed_pdb_path}")

        # 如果我们转换了 CIF，删除临时的转换 PDB
        if processing_file != input_file and processing_file.exists():
            try:
                processing_file.unlink()
            except:
                pass

        # 使用修复后的 PDB 进行后续步骤
        processing_file = fixed_pdb_path

    except Exception as e:
        logger.error(
            f"PDBFixer failed for {input_file.name}: {e}. Proceeding with file: {processing_file}.", exc_info=True
        )
        # 如果 PDBFixer 失败，我们继续使用 processing_file（可能是转换后的 CIF 或原始 PDB）

    # 2. 运行 PropKa 分析和质子化
    # 使用 PropKa 计算 pKa 并写入具有正确质子化的新 PDB
    try:
        logger.info(f"Running PropKa analysis for {processing_file.name} at pH {ph}")

        propka_pdb_path = output_file.parent / f"{input_file.stem}_propka.pdb"

        # PropKa 参数
        # args = [input_pdb, "--pH", str(pH), "--quiet", "--display-coupled-residues"]
        args = [str(processing_file), "--pH", str(ph), "--quiet", "--display-coupled-residues"]

        options, _ = loadOptions(args)
        parameters = Parameters(options.parameters)

        mol_container = MolecularContainer(options, parameters)
        mol_container.load_pdb()
        mol_container.calculate_pka()

        # 写入带有 PropKa 质子化的 PDB
        mol_container.write_pdb(str(propka_pdb_path))

        logger.info(f"PropKa completed. Saved to: {propka_pdb_path}")

        # 如果成功创建了 propka pdb，清理修复后的 pdb
        if processing_file == fixed_pdb_path and processing_file.exists():
            try:
                processing_file.unlink()
            except:
                pass

        # 更新处理文件以指向 PropKa 输出
        processing_file = propka_pdb_path

    except Exception as e:
        logger.error(
            f"PropKa analysis failed for {input_file.name}: {e}. Proceeding with previous file.", exc_info=True
        )

    # 3. 使用 Meeko (CLI) 进行准备
    logger.info(f"Preparing receptor using Meeko CLI: {output_file.name}")

    def run_openbabel_fallback(error_msg: str) -> bool:
        """Helper to run OpenBabel fallback."""
        logger.warning(f"Meeko CLI failed ({error_msg}), attempting fallback to OpenBabel...")
        try:
            # 检查 openbabel 绑定是否可用
            if openbabel:
                logger.info("Using OpenBabel Python bindings for fallback.")
                obConversion = openbabel.OBConversion()
                if not obConversion.SetInAndOutFormats("pdb", "pdbqt"):
                    raise RuntimeError("Failed to set OpenBabel formats")

                mol = openbabel.OBMol()

                if not obConversion.ReadFile(mol, str(processing_file)):
                    raise RuntimeError(f"OpenBabel failed to read {processing_file}")

                # -xr: 刚性分子
                obConversion.AddOption("r", openbabel.OBConversion.OUTOPTIONS)

                # 如果需要计算电荷（Gasteiger 通常是默认值）
                if charge_model == "gasteiger":
                    mol.AddHydrogens()  # 确保识别氢

                if not obConversion.WriteFile(mol, str(output_file)):
                    raise RuntimeError(f"OpenBabel failed to write {output_file}")

                logger.info(f"OpenBabel fallback successful: {output_file}")
                return True

            else:
                # 尝试 CLI 'obabel'
                logger.info("OpenBabel Python bindings not found, trying CLI 'obabel'...")
                obabel_cmd = ["obabel", str(processing_file), "-O", str(output_file), "-xr"]

                run_command(obabel_cmd, check=True, capture_output=True)
                logger.info(f"OpenBabel CLI fallback successful: {output_file}")
                return True

        except Exception as e_ob:
            logger.error(f"OpenBabel fallback also failed: {e_ob}")
            return False

    # 通过子进程运行 mk_prepare_receptor 以获得更好的稳定性和平台兼容性
    # 使用 sys.executable 确保在相同的 python 环境中运行
    cmd = [
        sys.executable,
        "-m",
        "meeko.cli.mk_prepare_receptor",
        "--read_pdb",
        str(processing_file),
        "--write_pdbqt",
        str(output_file),
        "--charge_model",
        charge_model,  # 使用指定的电荷模型
        # 注意：mk_prepare_receptor 不容易暴露 hydrate/rigid_macrocycles 选项
        # 但默认值通常对对接是合理的。
    ]

    try:
        # 运行命令并捕获输出
        # 直接使用 subprocess.run 以兼容标准库
        result = run_command(cmd, capture_output=True, text=True, check=True)
        logger.debug(f"Meeko CLI stdout: {result.stdout}")

    except CalledProcessError as e:
        logger.error(f"Meeko CLI failed with exit code {e.returncode}")
        # 仅当 stderr 不为空字符串时记录
        if e.output:
            logger.error(f"Meeko CLI stdout: {e.output}")
        if e.stderr:
            logger.error(f"Meeko CLI stderr: {e.stderr}")

        if not run_openbabel_fallback(f"Exit code {e.returncode}: {e.stderr}"):
            raise RuntimeError(f"Meeko CLI failed for {input_file.name}: {e.stderr}")

    except Exception as e:
        logger.error(f"Meeko CLI failed: {e}")
        # 如果可用，尝试提取输出
        if hasattr(e, "stdout") and e.stdout:
            logger.error(f"Meeko CLI stdout: {e.stdout}")
        if hasattr(e, "stderr") and e.stderr:
            logger.error(f"Meeko CLI stderr: {e.stderr}")

        if not run_openbabel_fallback(str(e)):
            raise RuntimeError(f"Meeko failed ({e}) AND OpenBabel fallback failed")

    # 检查输出文件是否存在
    if not output_file.exists():
        # 有时 Meeko 可能会附加后缀或静默失败？
        # 检查 output_file.stem + "_rigid.pdbqt" 或类似？
        # 如果未指定 flexres，它应该写入确切的文件名。
        # 列出目录看看发生了什么？
        logger.error(f"Meeko/OpenBabel CLI finished but output file not found: {output_file}")
        raise RuntimeError(f"Receptor preparation failed to generate output: {output_file}")

    # 清理临时 propka 文件
    if processing_file == propka_pdb_path and processing_file.exists():
        try:
            processing_file.unlink()
        except:
            pass

    return output_file


def get_box_from_ligand(ligand_file: Path, padding: float = 4.0) -> tuple[list[float], list[float]]:
    """
    zh: 根据参考配体计算网格盒中心和大小。
    en: Calculate grid box center and size from reference ligand.

    Args:
        ligand_file (Path):
            zh: 配体文件路径。
            en: Path to ligand file.
        padding (float, optional):
            zh: 额外的填充 (Angstrom)。默认为 4.0。
            en: Extra padding (Angstrom). Defaults to 4.0.

    Returns:
        tuple[list[float], list[float]]:
            zh: (中心, 大小) 列表。
            en: (center, size) lists.

    Raises:
        FileNotFoundError:
            zh: 如果配体文件不存在。
            en: If ligand file does not exist.
        ValueError:
            zh: 如果无法读取配体坐标。
            en: If ligand coordinates cannot be read.
    """
    ligand_file = Path(ligand_file)
    if not ligand_file.exists():
        raise FileNotFoundError(f"Ligand file for autobox not found: {ligand_file}")

    ext = ligand_file.suffix.lower()
    mol = None

    try:
        if ext == ".sdf":
            suppl = Chem.SDMolSupplier(str(ligand_file))
            try:
                mol = next(suppl)
            except StopIteration:
                logger.warning(f"SDF file empty: {ligand_file}")
        elif ext == ".pdb":
            mol = Chem.MolFromPDBFile(str(ligand_file))
        elif ext == ".mol2":
            mol = Chem.MolFromMol2File(str(ligand_file))
    except Exception as e:
        logger.warning(f"Failed to read ligand with RDKit: {e}")

    coords = []
    if mol:
        conf = mol.GetConformer()
        coords = conf.GetPositions()
    else:
        # PDBQT/PDB 的回退文本解析
        logger.info(f"Using text parsing for coordinates: {ligand_file}")
        with open(ligand_file) as f:
            for line in f:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    try:
                        x = float(line[30:38])
                        y = float(line[38:46])
                        z = float(line[46:54])
                        coords.append([x, y, z])
                    except ValueError:
                        pass
                # 对于 SDF/MOL2 的简单回退（如果 RDKit 失败）
                # 这很难通用，但可以尝试简单的块解析
                # 但目前假设如果 RDKit 失败且不是 PDB/PDBQT，我们可能无法获取坐标

    coords = np.array(coords)
    if coords.size == 0:
        raise ValueError(f"No valid coordinates found in ligand file: {ligand_file}")

    min_coords = coords.min(axis=0)
    max_coords = coords.max(axis=0)

    center = (min_coords + max_coords) / 2
    size = (max_coords - min_coords) + padding

    logger.info(f"Calculated box: center={center}, size={size}")
    return center.tolist(), size.tolist()


def get_box_from_receptor(receptor_file: Path, padding: float = 0.0) -> tuple[list[float], list[float]]:
    """
    zh: 根据受体计算最小外接盒中心和大小。
    en: Calculate bounding box center and size from receptor.

    Args:
        receptor_file (Path):
            zh: 受体文件路径 (PDB/PDBQT)。
            en: Path to receptor file (PDB/PDBQT).
        padding (float, optional):
            zh: 额外的填充 (Angstrom)。默认为 0.0。
            en: Extra padding (Angstrom). Defaults to 0.0.

    Returns:
        tuple[list[float], list[float]]:
            zh: (中心, 大小) 列表。
            en: (center, size) lists.

    Raises:
        FileNotFoundError:
            zh: 如果受体文件不存在。
            en: If receptor file does not exist.
        ValueError:
            zh: 如果无法解析受体坐标。
            en: If receptor coordinates cannot be parsed.
    """
    receptor_file = Path(receptor_file)
    if not receptor_file.exists():
        raise FileNotFoundError(f"Receptor file not found: {receptor_file}")

    coords = []
    # 简单的 PDB/PDBQT 解析
    # 我们不需要 RDKit 来解析整个受体，只需要原子坐标
    try:
        with open(receptor_file) as f:
            for line in f:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    try:
                        x = float(line[30:38])
                        y = float(line[38:46])
                        z = float(line[46:54])
                        coords.append([x, y, z])
                    except ValueError:
                        pass
    except Exception as e:
        logger.error(f"Failed to parse receptor coordinates: {e}")
        raise

    if not coords:
        raise ValueError(f"No valid atom coordinates found in receptor: {receptor_file}")

    coords_np = np.array(coords)
    min_coords = coords_np.min(axis=0)
    max_coords = coords_np.max(axis=0)

    center = (min_coords + max_coords) / 2
    size = (max_coords - min_coords) + padding

    # 确保 size 至少为正值，并保留一定余量
    # Vina 通常需要稍微大一点的盒子，或者至少不能是 0
    size = np.maximum(size, [10.0, 10.0, 10.0])

    logger.info(f"Calculated box from receptor: center={center}, size={size}")
    return center.tolist(), size.tolist()
