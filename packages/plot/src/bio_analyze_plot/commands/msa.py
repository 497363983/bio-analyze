import json
from pathlib import Path
import typer

from bio_analyze_core.logging import get_logger
from ..plots.msa import MsaPlot

logger = get_logger(__name__)

def msa_cmd(
    input_file: Path = typer.Option(
        ...,
        "-i", "--input",
        help="zh: 输入的MSA文件路径(FASTA格式)\nen: Path to the input MSA file (FASTA)"
    ),
    output_file: Path = typer.Option(
        ...,
        "-o", "--output",
        help="zh: 输出图片路径\nen: Output image path"
    ),
    seq_type: str = typer.Option(
        "aa",
        "--seq-type",
        help="zh: 序列类型(aa/nt)\nen: Sequence type (aa/nt)"
    ),
    show_logo: bool = typer.Option(
        True,
        "--show-logo/--no-logo",
        help="zh: 是否在顶部显示保守性Logo\nen: Whether to show a conservation logo at the top"
    ),
    theme: str = typer.Option(
        "default",
        "--theme",
        help="zh: 绘图主题(default/nature/science)\nen: Plot theme (default/nature/science)"
    ),
    font_size: int = typer.Option(
        10,
        "--font-size",
        help="zh: 字体大小\nen: Font size"
    ),
    bases_per_line: int = typer.Option(
        0,
        "--bases-per-line",
        min=0,
        help="zh: 每行显示的碱基/氨基酸数，0表示不换行\nen: Residues per line for wrapping, 0 means no wrap"
    ),
    base_colors: str = typer.Option(
        None,
        "--base-colors",
        help="zh: 自定义碱基/氨基酸颜色JSON映射，如'{\"A\":\"#000000\"}'\nen: JSON mapping for custom residue colors, e.g. '{\"A\":\"#000000\"}'"
    )
):
    """
    zh: 绘制多序列比对(MSA)图
    en: Plot a Multiple Sequence Alignment (MSA)
    """
    logger.info(f"Plotting MSA for {input_file}")
    
    try:
        parsed_base_colors = None
        if base_colors:
            parsed_base_colors = json.loads(base_colors)
            if not isinstance(parsed_base_colors, dict):
                raise ValueError("base_colors must be a JSON object mapping bases to colors")
        plotter = MsaPlot(theme=theme)
        plotter.plot(
            data=str(input_file),
            output=str(output_file),
            seq_type=seq_type,
            show_logo=show_logo,
            font_size=font_size,
            bases_per_line=bases_per_line or None,
            base_colors=parsed_base_colors
        )
        logger.info(f"MSA plot saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to plot MSA: {e}")
        raise typer.Exit(1)
