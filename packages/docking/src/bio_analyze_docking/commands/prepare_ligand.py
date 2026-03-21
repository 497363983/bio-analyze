from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_docking.prep import prepare_ligand


def prepare_ligand_cmd(
    input_file: Path = typer.Argument(
        ..., help="zh: 输入配体文件 (SDF, SMILES, PDB)。\nen: Input ligand file (SDF, SMILES, PDB)."
    ),
    output_file: Path = typer.Option(..., "-o", "--output", help="zh: 输出 PDBQT 文件。\nen: Output PDBQT file."),
    add_hydrogens: bool = typer.Option(True, help="zh: 添加氢原子。\nen: Add hydrogens."),
) -> None:
    """
    zh: 准备配体用于对接 (SDF/SMILES -> PDBQT)。
    en: Prepare ligand for docking (SDF/SMILES -> PDBQT).

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
    """
    prepare_ligand(input_file, output_file, add_hydrogens=add_hydrogens)
    typer.echo(f"Ligand prepared: {output_file}")
