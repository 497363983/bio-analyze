import pandas as pd
import numpy as np
from pathlib import Path
from bio_plot.plots.line import LinePlot
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')

def test_latex_support():
    # 测试 LaTeX 公式渲染
    data = pd.DataFrame({
        "x": np.linspace(0, 10, 20),
        "y": np.sin(np.linspace(0, 10, 20))
    })
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "latex_test.png"
    
    plotter = LinePlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="x",
        y="y",
        # 使用 LaTeX 公式作为标题和轴标签
        title=r"Sin Wave: $y = \sin(x)$",
        xlabel=r"Time ($t$)",
        ylabel=r"Amplitude ($\alpha$)",
        output=str(output_file)
    )
    
    # 这里我们主要验证代码能运行不报错，且文件生成。
    # 视觉验证需要查看图片。
    
    assert isinstance(fig, Figure)
    assert output_file.exists()
