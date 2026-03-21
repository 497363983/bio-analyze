from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from bio_analyze_core.utils import load_config
from bio_analyze_docking.api import run_docking, run_docking_batch


def execute_docking_cli(
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
