from pathlib import Path

import matplotlib
import pandas as pd
from bio_analyze_plot.plots.bar import BarPlot
from bio_analyze_plot.plots.volcano import VolcanoPlot
from matplotlib.figure import Figure

matplotlib.use("Agg")


def test_chinese_support_bar():
    # 测试柱状图的中文支持
    data = pd.DataFrame({"类别": ["A类", "B类", "C类"], "数值": [10, 20, 15], "分组": ["测试1", "测试1", "测试2"]})

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "bar_chinese.png"

    plotter = BarPlot(theme="nature")
    fig = plotter.plot(data=data, x="类别", y="数值", hue="分组", title="中文柱状图测试", output=str(output_file))

    assert isinstance(fig, Figure)
    assert output_file.exists()


def test_chinese_support_volcano():
    # 测试火山图的中文支持
    data = pd.DataFrame(
        {
            "fold_change": [2.5, -3.0, 0.5],
            "p_value": [0.001, 0.0001, 0.5],
            "gene": ["基因A", "基因B", "基因C"],
        }
    )

    output_dir = Path(__file__).parent / "output"
    output_file = output_dir / "volcano_chinese.png"

    plotter = VolcanoPlot(theme="default")
    fig = plotter.plot(data=data, x="fold_change", y="p_value", title="中文火山图测试", output=str(output_file))

    assert isinstance(fig, Figure)
    assert output_file.exists()
