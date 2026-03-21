from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from bio_analyze_docking.commands.utils import execute_docking_cli


def run_haddock_cmd(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="zh: 配置文件路径。\nen: Config file path."
    ),
    receptor: Optional[Path] = typer.Option(
        None, "-r", "--receptor", help="zh: 受体文件/目录。\nen: Receptor file/dir."
    ),
    ligand: Optional[Path] = typer.Option(None, "-l", "--ligand", help="zh: 配体文件/目录。\nen: Ligand file/dir."),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output", help="zh: 输出目录。\nen: Output dir."),
    n_poses: Optional[int] = typer.Option(None, help="zh: 采样的姿态数量。\nen: Number of poses to sample."),
    charge_model: Optional[str] = typer.Option(None, "--charge-model", help="zh: 电荷模型。\nen: Charge model."),
    haddock_config: Optional[Path] = typer.Option(
        None,
        "--haddock-config",
        help="zh: 自定义 HADDOCK3 配置文件路径。\nen: Custom HADDOCK3 configuration file path.",
    ),
) -> None:
    """
    zh: 使用 HADDOCK 引擎运行分子对接。
    en: Run molecular docking using HADDOCK engine.
    """
    # Haddock 不使用 Box 参数，也不使用 exhaustiveness
    execute_docking_cli(
        "haddock",
        config_file,
        receptor,
        ligand,
        output_dir,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        100,
        n_poses,
        charge_model,
        haddock_config,
    )
