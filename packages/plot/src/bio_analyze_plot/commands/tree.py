from pathlib import Path
import typer

from bio_analyze_core.logging import get_logger
from ..plots.tree import TreePlot

logger = get_logger(__name__)

def tree_cmd(
    input_file: Path = typer.Option(
        ...,
        "-i", "--input",
        help="zh: 输入的树文件路径(Newick格式)\nen: Path to the input tree file (Newick format)"
    ),
    output_file: Path = typer.Option(
        ...,
        "-o", "--output",
        help="zh: 输出图片路径\nen: Output image path"
    ),
    format: str = typer.Option(
        "newick",
        "--format",
        help="zh: 树文件格式(newick/nexus)\nen: Tree file format (newick/nexus)"
    ),
    layout: str = typer.Option(
        "rectangular",
        "--layout",
        help="zh: 树图布局(rectangular/circular)\nen: Tree layout (rectangular/circular)"
    ),
    show_confidence: bool = typer.Option(
        True,
        "--show-confidence/--no-confidence",
        help="zh: 是否显示分支支持率(Bootstrap值)\nen: Whether to show branch support values"
    ),
    theme: str = typer.Option(
        "default",
        "--theme",
        help="zh: 绘图主题(default/nature/science)\nen: Plot theme (default/nature/science)"
    ),
    branch_thickness: float = typer.Option(
        1.0,
        "--branch-thickness",
        help="zh: 分支线条粗细\nen: Branch line thickness"
    ),
    font_size: int = typer.Option(
        10,
        "--font-size",
        help="zh: 字体大小\nen: Font size"
    ),
    label_offset_scale: float = typer.Option(
        0.05,
        "--label-offset-scale",
        min=0.001,
        help="zh: 标签相对偏移比例\nen: Relative label offset scale"
    ),
    label_bbox_alpha: float = typer.Option(
        0.65,
        "--label-bbox-alpha",
        min=0.0,
        max=1.0,
        help="zh: 标签背景透明度(0-1)\nen: Label background alpha (0-1)"
    )
):
    """
    zh: 绘制系统发育树图
    en: Plot a phylogenetic tree
    """
    logger.info(f"Plotting phylogenetic tree for {input_file}")
    
    try:
        plotter = TreePlot(theme=theme)
        plotter.plot(
            data=str(input_file),
            output=str(output_file),
            format=format,
            layout=layout,
            show_confidence=show_confidence,
            branch_thickness=branch_thickness,
            font_size=font_size,
            label_offset_scale=label_offset_scale,
            label_bbox_alpha=label_bbox_alpha
        )
        logger.info(f"Tree plot saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to plot tree: {e}")
        raise typer.Exit(1)
