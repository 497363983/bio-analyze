from __future__ import annotations

from pathlib import Path

import typer

from bio_analyze_docking.prep import prepare_receptor


def prepare_receptor_cmd(
    input_file: Path = typer.Argument(..., help="zh: 输入受体文件 (PDB)。\nen: Input receptor file (PDB)."),
    output_file: Path = typer.Option(..., "-o", "--output", help="zh: 输出 PDBQT 文件。\nen: Output PDBQT file."),
    add_hydrogens: bool = typer.Option(True, help="zh: 添加氢原子。\nen: Add hydrogens."),
    charge_model: str = typer.Option(
        "gasteiger",
        "--charge-model",
        help="zh: 电荷模型 (gasteiger, zero 等)。\nen: Charge model (gasteiger, zero, etc.).",
    ),
) -> None:
    """
    zh: 准备受体用于对接 (PDB -> PDBQT)。
    en: Prepare receptor for docking (PDB -> PDBQT).

    Args:
        input_file (Path):
            zh: 输入受体文件路径 (PDB/CIF)。
            en: Path to input receptor file (PDB/CIF).
        output_file (Path):
            zh: 输出 PDBQT 文件路径。
            en: Path to output PDBQT file.
        add_hydrogens (bool, optional):
            zh: 是否自动添加极性氢。默认为 True。
            en: Whether to automatically add polar hydrogens. Defaults to True.
        charge_model (str, optional):
            zh: 电荷计算模型 (gasteiger, kollman, zero)。默认为 'gasteiger'。
            en: Charge calculation model (gasteiger, kollman, zero). Defaults to 'gasteiger'.
    """
    prepare_receptor(input_file, output_file, add_hydrogens=add_hydrogens, charge_model=charge_model)
    typer.echo(f"Receptor prepared: {output_file}")
