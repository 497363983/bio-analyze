
from pathlib import Path

import numpy as np
import pandas as pd
from bio_analyze_plot.plots.scatter import ScatterPlot
from matplotlib.figure import Figure


def test_scatter_plot_generation():
    # Mock data
    np.random.seed(42)
    n_points = 50
    data = pd.DataFrame({
        "x": np.random.randn(n_points),
        "y": np.random.randn(n_points),
        "group": np.random.choice(["A", "B"], n_points),
        "size_col": np.random.rand(n_points) * 10
    })

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    plotter = ScatterPlot(theme="science")

    # Test 1: Basic scatter plot
    output_file_1 = output_dir / "scatter_basic.png"
    fig1 = plotter.plot(
        data=data, 
        x="x", 
        y="y", 
        hue="group", 
        output=str(output_file_1)
    )
    assert isinstance(fig1, Figure)
    assert output_file_1.exists()

    # Test 2: Scatter plot with ellipse
    output_file_2 = output_dir / "scatter_ellipse.png"
    fig2 = plotter.plot(
        data=data, 
        x="x", 
        y="y", 
        hue="group", 
        add_ellipse=True,
        output=str(output_file_2)
    )
    assert isinstance(fig2, Figure)
    assert output_file_2.exists()
    
    # Test 3: Scatter plot with size and style
    output_file_3 = output_dir / "scatter_complex.png"
    fig3 = plotter.plot(
        data=data,
        x="x",
        y="y",
        hue="group",
        style="group",
        size="size_col",
        output=str(output_file_3)
    )
    assert isinstance(fig3, Figure)
    assert output_file_3.exists()
