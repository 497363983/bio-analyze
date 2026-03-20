from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

matplotlib.use("Agg")

from bio_analyze_plot.plots.bar import BarPlot
from bio_analyze_plot.plots.heatmap import HeatmapPlot
from bio_analyze_plot.plots.line import LinePlot
from bio_analyze_plot.plots.pca import PCAPlot
from bio_analyze_plot.plots.volcano import VolcanoPlot
from bio_analyze_plot.theme import THEMES


# ??????
@pytest.fixture
def test_data():
    df_bar = pd.DataFrame({"group": ["A", "B"], "value": [10, 20]})
    df_line = pd.DataFrame({"x": range(10), "y": np.sin(range(10)), "group": ["A"] * 5 + ["B"] * 5})
    df_heatmap = pd.DataFrame(np.random.rand(10, 5), columns=[f"S{i}" for i in range(5)])
    df_volcano = pd.DataFrame({"log2FoldChange": np.random.randn(100), "padj": np.random.rand(100)})
    df_pca = pd.DataFrame(np.random.rand(10, 5), columns=[f"S{i}" for i in range(5)])
    return df_bar, df_line, df_heatmap, df_volcano, df_pca


def test_all_themes_all_plots(test_data):
    """
    ?????????????????
    """
    df_bar, df_line, df_heatmap, df_volcano, df_pca = test_data

    themes = list(THEMES.keys())  # ["default", "nature", "science"]

    output_base = Path(__file__).parent / "output"
    output_base.mkdir(exist_ok=True)

    for theme_name in themes:
        print(f"Testing theme: {theme_name}")

        # ?????????
        theme_dir = output_base / theme_name
        theme_dir.mkdir(exist_ok=True)

        # 1. Bar Plot
        plotter = BarPlot(theme=theme_name)
        out = theme_dir / "bar.png"
        fig = plotter.plot(data=df_bar, x="group", y="value", output=str(out))
        assert isinstance(fig, Figure)
        assert out.exists()

        # 2. Line Plot
        plotter = LinePlot(theme=theme_name)
        out = theme_dir / "line.png"
        fig = plotter.plot(data=df_line, x="x", y="y", hue="group", output=str(out))
        assert isinstance(fig, Figure)
        assert out.exists()

        # 3. Heatmap
        plotter = HeatmapPlot(theme=theme_name)
        out = theme_dir / "heatmap.png"
        fig = plotter.plot(data=df_heatmap, output=str(out))
        assert isinstance(fig, Figure)
        assert out.exists()

        # 4. Volcano
        plotter = VolcanoPlot(theme=theme_name)
        out = theme_dir / "volcano.png"
        fig = plotter.plot(data=df_volcano, y="padj", output=str(out))
        assert isinstance(fig, Figure)
        assert out.exists()

        # 5. PCA
        plotter = PCAPlot(theme=theme_name)
        out = theme_dir / "pca.png"
        fig = plotter.plot(data=df_pca, transpose=True, output=str(out))
        assert isinstance(fig, Figure)
        assert out.exists()

        import matplotlib.pyplot as plt

        plt.close("all")
