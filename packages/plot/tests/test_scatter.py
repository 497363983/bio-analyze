import numpy as np
import pandas as pd
import pytest
from bio_analyze_plot.plots.scatter import ScatterPlot
from matplotlib.figure import Figure


@pytest.fixture
def scatter_data():
    # Mock data
    # Seed is handled by conftest.py
    n_points = 50
    return pd.DataFrame({
        "x": np.random.randn(n_points),
        "y": np.random.randn(n_points),
        "group": np.random.choice(["A", "B"], n_points),
        "size_col": np.random.rand(n_points) * 10
    })


def test_scatter_basic(scatter_data, check_plot, tmp_path):
    plotter = ScatterPlot(theme="science")

    # Test 1: Basic scatter plot
    output_file_1 = tmp_path / "scatter_basic.png"
    fig1 = plotter.plot(
        data=scatter_data, 
        x="x", 
        y="y", 
        hue="group", 
        output=str(output_file_1)
    )
    assert output_file_1.exists()
    check_plot(fig1)


def test_scatter_ellipse(scatter_data, check_plot, tmp_path):
    plotter = ScatterPlot(theme="science")

    # Test 2: Scatter plot with ellipse
    output_file_2 = tmp_path / "scatter_ellipse.png"
    fig2 = plotter.plot(
        data=scatter_data, 
        x="x", 
        y="y", 
        hue="group", 
        add_ellipse=True,
        output=str(output_file_2)
    )
    assert output_file_2.exists()
    check_plot(fig2)


def test_scatter_complex(scatter_data, check_plot, tmp_path):
    plotter = ScatterPlot(theme="science")

    # Test 3: Scatter plot with size and style
    output_file_3 = tmp_path / "scatter_complex.png"
    fig3 = plotter.plot(
        data=scatter_data,
        x="x",
        y="y",
        hue="group",
        style="group",
        size="size_col",
        output=str(output_file_3)
    )
    assert output_file_3.exists()
    check_plot(fig3)
