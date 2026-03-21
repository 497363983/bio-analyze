from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from bio_analyze_docking.commands.utils import execute_docking_cli


def run_vina_cmd(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="zh: 配置文件路径。\nen: Config file path."
    ),
    receptor: Optional[Path] = typer.Option(
        None, "-r", "--receptor", help="zh: 受体文件/目录。\nen: Receptor file/dir."
    ),
    ligand: Optional[Path] = typer.Option(None, "-l", "--ligand", help="zh: 配体文件/目录。\nen: Ligand file/dir."),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output", help="zh: 输出目录。\nen: Output dir."),
    center_x: Optional[float] = typer.Option(None, help="zh: 盒子中心 X。\nen: Box center X."),
    center_y: Optional[float] = typer.Option(None, help="zh: 盒子中心 Y。\nen: Box center Y."),
    center_z: Optional[float] = typer.Option(None, help="zh: 盒子中心 Z。\nen: Box center Z."),
    size_x: Optional[float] = typer.Option(None, help="zh: 盒子大小 X。\nen: Box size X."),
    size_y: Optional[float] = typer.Option(None, help="zh: 盒子大小 Y。\nen: Box size Y."),
    size_z: Optional[float] = typer.Option(None, help="zh: 盒子大小 Z。\nen: Box size Z."),
    autobox_ligand: Optional[Path] = typer.Option(None, help="zh: 参考配体。\nen: Reference ligand."),
    padding: Optional[float] = typer.Option(None, help="zh: 自动盒填充。\nen: Autobox padding."),
    exhaustiveness: Optional[int] = typer.Option(None, help="zh: 对接穷尽性。\nen: Exhaustiveness."),
    n_poses: Optional[int] = typer.Option(None, help="zh: 生成的姿态数量。\nen: Number of poses."),
    charge_model: Optional[str] = typer.Option(None, "--charge-model", help="zh: 电荷模型。\nen: Charge model."),
) -> None:
    """
    zh: 使用 Vina 引擎运行分子对接。
    en: Run molecular docking using Vina engine.
    """
    execute_docking_cli(
        "vina",
        config_file,
        receptor,
        ligand,
        output_dir,
        center_x,
        center_y,
        center_z,
        size_x,
        size_y,
        size_z,
        autobox_ligand,
        padding,
        exhaustiveness,
        n_poses,
        charge_model,
    )
