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

    run_app = typer.Typer(help="zh: 运行分子对接流程。\nen: Run molecular docking pipeline.")
    app.add_typer(run_app, name="run")

    def _execute_docking_cli(
        engine: str,
        config_file: Optional[Path],
        receptor: Optional[Path],
        ligand: Optional[Path],
        output_dir: Optional[Path],
        center_x: Optional[float] = None,
        center_y: Optional[float] = None,
        center_z: Optional[float] = None,
        size_x: Optional[float] = None,
        size_y: Optional[float] = None,
        size_z: Optional[float] = None,
        autobox_ligand: Optional[Path] = None,
        padding: Optional[float] = 4.0,
        exhaustiveness: Optional[int] = 8,
        n_poses: Optional[int] = 9,
        charge_model: Optional[str] = "gasteiger",
        haddock_config: Optional[Path] = None,
    ):
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
        def get_param(cli_val, config_key, default=None):
            if cli_val is not None:
                return cli_val
            if config_key in config:
                return config[config_key]
            return default

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

        if not p_receptor or not p_ligand or not p_output_dir:
            typer.echo(
                "Error: Missing required arguments: --receptor, --ligand, or --output (or in config file).", err=True
            )
            raise typer.Exit(code=1)

        p_center_x = get_param(center_x, "center_x")
        p_center_y = get_param(center_y, "center_y")
        p_center_z = get_param(center_z, "center_z")

        p_size_x = get_param(size_x, "size_x")
        p_size_y = get_param(size_y, "size_y")
        p_size_z = get_param(size_z, "size_z")

        if p_center_x is not None:
            p_size_x = p_size_x if p_size_x is not None else 20.0
            p_size_y = p_size_y if p_size_y is not None else 20.0
            p_size_z = p_size_z if p_size_z is not None else 20.0

        p_padding = get_param(padding, "padding", 4.0)
        p_exhaustiveness = get_param(exhaustiveness, "exhaustiveness", 8)
        p_n_poses = get_param(n_poses, "n_poses", 9)
        p_charge_model = get_param(charge_model, "charge_model", "gasteiger")
        p_haddock_config = get_param(haddock_config, "haddock_config")

        if p_haddock_config:
            p_haddock_config = Path(p_haddock_config)

        p_output_dir.mkdir(parents=True, exist_ok=True)

        center = None
        size = None

        if p_size_x and p_size_y and p_size_z:
            size = [float(p_size_x), float(p_size_y), float(p_size_z)]

        if p_autobox_ligand:
            pass
        elif p_center_x is not None and p_center_y is not None and p_center_z is not None:
            center = [float(p_center_x), float(p_center_y), float(p_center_z)]
        else:
            if not p_autobox_ligand and engine != "haddock":
                typer.echo("Info: No box parameters provided. Docking box will be calculated from receptor.", err=True)

        is_batch = p_receptor.is_dir() or p_ligand.is_dir()
        p_boxes = get_param(None, "boxes", {})

        if is_batch:
            typer.echo(f"Running {engine} in batch mode...")
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
                engine=engine,
                boxes=p_boxes,
                haddock_config=p_haddock_config,
            )
            typer.echo(f"\nBatch docking completed. Processed {len(results)} pairs.")
            success_count = sum(1 for r in results if r.get("status") == "success")
            typer.echo(f"Successful: {success_count}/{len(results)}")
            summary_file = p_output_dir / "docking_summary.csv"
            typer.echo(f"Summary saved to: {summary_file}")
        else:
            typer.echo(f"Running {engine} single docking...")
            if p_receptor and p_boxes:
                box_config = p_boxes.get(p_receptor.name) or p_boxes.get(p_receptor.stem)
                if box_config:
                    if "center_x" in box_config and "center_y" in box_config and "center_z" in box_config:
                        center = [
                            float(box_config["center_x"]),
                            float(box_config["center_y"]),
                            float(box_config["center_z"]),
                        ]
                    if "size_x" in box_config and "size_y" in box_config and "size_z" in box_config:
                        size = [float(box_config["size_x"]), float(box_config["size_y"]), float(box_config["size_z"])]

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
                    engine=engine,
                    haddock_config=p_haddock_config,
                )
                typer.echo("Docking completed successfully!")
                typer.echo(f"Best Score: {res['best_score']}")
                typer.echo(f"Output saved to: {res['output_file']}")
                if res.get("box_center"):
                    typer.echo(f"Box Center: {res['box_center']}")
                    typer.echo(f"Box Size:   {res['box_size']}")
            except Exception as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(code=1)

    @run_app.command("vina")
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
        _execute_docking_cli(
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

    @run_app.command("smina")
    def run_smina_cmd(
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
        zh: 使用 Smina 引擎运行分子对接。
        en: Run molecular docking using Smina engine.
        """
        _execute_docking_cli(
            "smina",
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

    @run_app.command("gnina")
    def run_gnina_cmd(
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
        zh: 使用 Gnina 引擎运行分子对接。
        en: Run molecular docking using Gnina engine.
        """
        _execute_docking_cli(
            "gnina",
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

    @run_app.command("haddock")
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
        _execute_docking_cli(
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

    localize_app(app, detect_language())
    return app
