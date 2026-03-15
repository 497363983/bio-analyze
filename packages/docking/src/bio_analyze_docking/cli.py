from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from bio_analyze_core.cli_i18n import detect_language, localize_app
from bio_analyze_core.utils import load_config

from .api import run_docking, run_docking_batch
from .prep import prepare_ligand, prepare_receptor


def get_app() -> typer.Typer:
    """
    zh: 获取 Docking 模块的 Typer 应用实例。
    en: Get the Typer app instance for the Docking module.

    Returns:
        typer.Typer:
            zh: 配置好的 Typer 应用。
            en: Configured Typer app.
    """
    app = typer.Typer(help="zh: 分子对接工具。\nen: Molecular docking tools.")

    @app.command("prepare-receptor")
    def _prepare_receptor(
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

    @app.command("prepare-ligand")
    def _prepare_ligand(
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

    @app.command("run")
    def _run(
        config_file: Optional[Path] = typer.Option(
            None, "--config", "-c", help="zh: 配置文件路径 (JSON/YAML)。\nen: Path to config file (JSON/YAML)."
        ),
        receptor: Optional[Path] = typer.Option(
            None, "-r", "--receptor", help="zh: 受体文件/目录 (PDB/PDBQT)。\nen: Receptor file/directory (PDB/PDBQT)."
        ),
        ligand: Optional[Path] = typer.Option(
            None,
            "-l",
            "--ligand",
            help="zh: 配体文件/目录 (SDF/SMILES/PDBQT)。\nen: Ligand file/directory (SDF/SMILES/PDBQT).",
        ),
        output_dir: Optional[Path] = typer.Option(None, "-o", "--output", help="zh: 输出目录。\nen: Output directory."),
        center_x: Optional[float] = typer.Option(None, help="zh: 盒子中心 X。\nen: Box center X."),
        center_y: Optional[float] = typer.Option(None, help="zh: 盒子中心 Y。\nen: Box center Y."),
        center_z: Optional[float] = typer.Option(None, help="zh: 盒子中心 Z。\nen: Box center Z."),
        size_x: Optional[float] = typer.Option(None, help="zh: 盒子大小 X。\nen: Box size X."),
        size_y: Optional[float] = typer.Option(None, help="zh: 盒子大小 Y。\nen: Box size Y."),
        size_z: Optional[float] = typer.Option(None, help="zh: 盒子大小 Z。\nen: Box size Z."),
        autobox_ligand: Optional[Path] = typer.Option(
            None,
            help="zh: 用于定义网格盒子的参考配体 (覆盖 center/size)。\nen: Reference ligand for defining grid box (overrides center/size).",
        ),
        padding: Optional[float] = typer.Option(None, help="zh: 自动盒填充。\nen: Autobox padding."),
        exhaustiveness: Optional[int] = typer.Option(None, help="zh: 对接穷尽性。\nen: Docking exhaustiveness."),
        n_poses: Optional[int] = typer.Option(None, help="zh: 生成的姿态数量。\nen: Number of poses to generate."),
        charge_model: Optional[str] = typer.Option(
            None, "--charge-model", help="zh: 受体准备的电荷模型。\nen: Charge model for receptor preparation."
        ),
        engine: Optional[str] = typer.Option(
            None, "--engine", help="zh: 对接引擎 (vina, gnina 等)。\nen: Docking engine (vina, gnina, etc.)."
        ),
    ) -> None:
        """
        zh: 运行分子对接流程。
        en: Run molecular docking pipeline.

        支持单个文件对接或批量对接（如果提供了目录）。
        支持通过 --config 加载 JSON/YAML 配置文件，命令行参数优先级更高。

        Args:
            config_file (Optional[Path], optional):
                zh: 配置文件路径。
                en: Configuration file path.
            receptor (Optional[Path], optional):
                zh: 受体文件或目录路径。
                en: Receptor file or directory path.
            ligand (Optional[Path], optional):
                zh: 配体文件或目录路径。
                en: Ligand file or directory path.
            output_dir (Optional[Path], optional):
                zh: 结果输出目录。
                en: Results output directory.
            center_x (Optional[float], optional):
                zh: 搜索空间中心 X 坐标。
                en: Search space center X coordinate.
            center_y (Optional[float], optional):
                zh: 搜索空间中心 Y 坐标。
                en: Search space center Y coordinate.
            center_z (Optional[float], optional):
                zh: 搜索空间中心 Z 坐标。
                en: Search space center Z coordinate.
            size_x (Optional[float], optional):
                zh: 搜索空间 X 轴尺寸 (Angstroms)。
                en: Search space size in X dimension (Angstroms).
            size_y (Optional[float], optional):
                zh: 搜索空间 Y 轴尺寸 (Angstroms)。
                en: Search space size in Y dimension (Angstroms).
            size_z (Optional[float], optional):
                zh: 搜索空间 Z 轴尺寸 (Angstroms)。
                en: Search space size in Z dimension (Angstroms).
            autobox_ligand (Optional[Path], optional):
                zh: 参考配体路径，用于自动确定搜索空间。
                en: Reference ligand path for automatically determining search space.
            padding (Optional[float], optional):
                zh: 自动计算盒子时的边缘填充 (Angstroms)。
                en: Padding for autobox calculation (Angstroms).
            exhaustiveness (Optional[int], optional):
                zh: 搜索穷尽性 (默认 8)。值越大越慢但可能更准确。
                en: Search exhaustiveness (default 8). Higher values are slower but potentially more accurate.
            n_poses (Optional[int], optional):
                zh: 保留的最佳姿态数量。
                en: Number of top poses to keep.
            charge_model (Optional[str], optional):
                zh: 受体预处理电荷模型。
                en: Receptor preprocessing charge model.
            engine (Optional[str], optional):
                zh: 对接引擎 ('vina', 'smina', 'gnina')。
                en: Docking engine ('vina', 'smina', 'gnina').
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

    localize_app(app, detect_language())
    return app
