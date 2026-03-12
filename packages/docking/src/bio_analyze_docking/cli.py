from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from bio_analyze_core.utils import load_config

from .api import run_docking, run_docking_batch
from .prep import prepare_ligand, prepare_receptor


def get_app() -> typer.Typer:
    app = typer.Typer(help="Molecular docking tools.")

    @app.command("prepare-receptor")
    def _prepare_receptor(
        input_file: Path = typer.Argument(..., help="输入受体文件 (PDB)。"),
        output_file: Path = typer.Option(..., "-o", "--output", help="输出 PDBQT 文件。"),
        add_hydrogens: bool = typer.Option(True, help="添加氢原子。"),
        charge_model: str = typer.Option("gasteiger", "--charge-model", help="电荷模型 (gasteiger, zero 等)。"),
    ) -> None:
        """准备受体用于对接 (PDB -> PDBQT)。"""
        prepare_receptor(input_file, output_file, add_hydrogens=add_hydrogens, charge_model=charge_model)
        typer.echo(f"Receptor prepared: {output_file}")

    @app.command("prepare-ligand")
    def _prepare_ligand(
        input_file: Path = typer.Argument(..., help="输入配体文件 (SDF, SMILES, PDB)。"),
        output_file: Path = typer.Option(..., "-o", "--output", help="输出 PDBQT 文件。"),
        add_hydrogens: bool = typer.Option(True, help="添加氢原子。"),
    ) -> None:
        """准备配体用于对接 (SDF/SMILES -> PDBQT)。"""
        prepare_ligand(input_file, output_file, add_hydrogens=add_hydrogens)
        typer.echo(f"Ligand prepared: {output_file}")

    @app.command("run")
    def _run(
        config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="配置文件路径 (JSON/YAML)。"),
        receptor: Optional[Path] = typer.Option(None, "-r", "--receptor", help="受体文件/目录 (PDB/PDBQT)。"),
        ligand: Optional[Path] = typer.Option(None, "-l", "--ligand", help="配体文件/目录 (SDF/SMILES/PDBQT)。"),
        output_dir: Optional[Path] = typer.Option(None, "-o", "--output", help="输出目录。"),
        center_x: Optional[float] = typer.Option(None, help="盒子中心 X。"),
        center_y: Optional[float] = typer.Option(None, help="盒子中心 Y。"),
        center_z: Optional[float] = typer.Option(None, help="盒子中心 Z。"),
        size_x: Optional[float] = typer.Option(None, help="盒子大小 X。"),
        size_y: Optional[float] = typer.Option(None, help="盒子大小 Y。"),
        size_z: Optional[float] = typer.Option(None, help="盒子大小 Z。"),
        autobox_ligand: Optional[Path] = typer.Option(None, help="用于定义网格盒子的参考配体 (覆盖 center/size)。"),
        padding: Optional[float] = typer.Option(None, help="自动盒填充。"),
        exhaustiveness: Optional[int] = typer.Option(None, help="对接穷尽性。"),
        n_poses: Optional[int] = typer.Option(None, help="生成的姿态数量。"),
        charge_model: Optional[str] = typer.Option(None, "--charge-model", help="受体准备的电荷模型。"),
        engine: Optional[str] = typer.Option(None, "--engine", help="对接引擎 (vina, gnina 等)。"),
    ) -> None:
        """
        运行分子对接流程。
        支持单个文件对接或批量对接（如果提供了目录）。
        支持通过 --config 加载 JSON/YAML 配置文件，命令行参数优先级更高。
        """
        # 1. 加载配置
        config = {}
        if config_file:
            try:
                config = load_config(config_file)
                typer.echo(f"Loaded configuration from {config_file}")
            except Exception as e:
                typer.echo(f"Error loading config: {e}", err=True)
                raise typer.Exit(code=1)

        # 2. 合并参数 (命令行 > 配置文件 > 默认值)
        # 辅助函数：获取最终值
        def get_param(cli_val, config_key, default=None):
            if cli_val is not None:
                return cli_val
            if config_key in config:
                return config[config_key]
            return default

        # 解析路径参数 (需要转换为 Path 对象)
        p_receptor = get_param(receptor, "receptor")
        p_ligand = get_param(ligand, "ligand")
        p_output_dir = get_param(output_dir, "output_dir")
        p_autobox_ligand = get_param(autobox_ligand, "autobox_ligand")

        if p_receptor:
            p_receptor = Path(p_receptor)
        if p_ligand:
            p_ligand = Path(p_ligand)
        if p_output_dir:
            p_output_dir = Path(p_output_dir)
        if p_autobox_ligand:
            p_autobox_ligand = Path(p_autobox_ligand)

        # 必需参数检查
        if not p_receptor or not p_ligand or not p_output_dir:
            typer.echo(
                "Error: Missing required arguments: --receptor, --ligand, or --output (or in config file).", err=True
            )
            raise typer.Exit(code=1)

        # 解析其他参数
        p_center_x = get_param(center_x, "center_x")
        p_center_y = get_param(center_y, "center_y")
        p_center_z = get_param(center_z, "center_z")

        # 盒子大小默认值处理 (如果 config 中没有，默认为 20.0)
        # 注意：如果我们要支持自动计算盒子，这里的默认值可能会干扰判断
        # 如果 CLI 没有提供，config 也没有，我们应该允许它是 None
        p_size_x = get_param(size_x, "size_x")
        p_size_y = get_param(size_y, "size_y")
        p_size_z = get_param(size_z, "size_z")

        # 只有在提供了 center 但没提供 size 的情况下，才使用默认值 20.0？
        # 或者，如果用户想要自动盒子，他们就不应该提供 size。
        # 让我们保持逻辑：如果提供了 center，必须有 size (或者默认 20)。
        # 如果没提供 center，也没 autobox_ligand，那么就是全受体对接，此时 size 应该也是自动计算的。

        if p_center_x is not None:
            p_size_x = p_size_x if p_size_x is not None else 20.0
            p_size_y = p_size_y if p_size_y is not None else 20.0
            p_size_z = p_size_z if p_size_z is not None else 20.0

        p_padding = get_param(padding, "padding", 4.0)
        p_exhaustiveness = get_param(exhaustiveness, "exhaustiveness", 8)
        p_n_poses = get_param(n_poses, "n_poses", 9)
        p_charge_model = get_param(charge_model, "charge_model", "gasteiger")
        p_engine = get_param(engine, "engine", "vina")

        p_output_dir.mkdir(parents=True, exist_ok=True)

        # 确定 Box 参数
        center = None
        size = None

        if p_size_x and p_size_y and p_size_z:
            size = [float(p_size_x), float(p_size_y), float(p_size_z)]

        if p_autobox_ligand:
            pass
        elif p_center_x is not None and p_center_y is not None and p_center_z is not None:
            center = [float(p_center_x), float(p_center_y), float(p_center_z)]
        else:
            # 如果都没有提供，run_docking 将自动根据受体计算盒子
            if not p_autobox_ligand:
                typer.echo("Info: No box parameters provided. Docking box will be calculated from receptor.", err=True)
                # raise typer.Exit(code=1) # 不再抛出错误

        # 检查批量模式
        is_batch = p_receptor.is_dir() or p_ligand.is_dir()

        if is_batch:
            typer.echo("Running in batch mode...")
            results = run_docking_batch(
                receptors=p_receptor,
                ligands=p_ligand,
                output_dir=p_output_dir,
                center=center,
                size=size,
                autobox_ligand=p_autobox_ligand,
                padding=float(p_padding),
                exhaustiveness=int(p_exhaustiveness),
                n_poses=int(p_n_poses),
                charge_model=p_charge_model,
                engine=p_engine,
            )

            # 打印摘要
            typer.echo(f"\nBatch docking completed. Processed {len(results)} pairs.")
            success_count = sum(1 for r in results if r.get("status") == "success")
            typer.echo(f"Successful: {success_count}/{len(results)}")

            summary_file = p_output_dir / "docking_summary.csv"
            typer.echo(f"Summary saved to: {summary_file}")

        else:
            # 单次运行
            typer.echo("Running single docking...")

            try:
                res = run_docking(
                    receptor=p_receptor,
                    ligand=p_ligand,
                    output_dir=p_output_dir,
                    center=center,
                    size=size,
                    autobox_ligand=p_autobox_ligand,
                    padding=float(p_padding),
                    exhaustiveness=int(p_exhaustiveness),
                    n_poses=int(p_n_poses),
                    charge_model=p_charge_model,
                    engine=p_engine,
                )
                typer.echo("Docking completed successfully!")
                typer.echo(f"Best Score: {res['best_score']} kcal/mol")
                typer.echo(f"Output saved to: {res['output_file']}")
                if res.get("box_center"):
                    typer.echo(f"Box Center: {res['box_center']}")
                    typer.echo(f"Box Size:   {res['box_size']}")

            except Exception as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(code=1)

    return app
