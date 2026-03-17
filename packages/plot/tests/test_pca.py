import numpy as np
import pandas as pd
from bio_analyze_plot.plots.pca import PCAPlot
from matplotlib.figure import Figure


def test_pca_plot(check_plot, tmp_path):
    # Create dummy expression data: 100 genes x 6 samples
    # Seed is handled by conftest.py
    data = np.random.rand(100, 6)
    # Add some structure: first 3 samples similar, last 3 similar
    data[:, 0:3] += 2

    df = pd.DataFrame(data, columns=["S1", "S2", "S3", "S4", "S5", "S6"])
    df.index.name = "Gene"

    output_file = tmp_path / "pca.png"

    # Groups
    groups = ["Control"] * 3 + ["Treated"] * 3

    plotter = PCAPlot(theme="nature")
    fig = plotter.plot(
        data=df,
        hue=groups,  # Pass list as hue
        transpose=True,  # Genes x Samples -> Samples x Genes
        title="Test PCA",
        output=str(output_file),
    )

    assert output_file.exists()
    check_plot(fig)


def test_pca_plot_tidy(check_plot, tmp_path):
    # Test tidy format (Samples x Genes) with hue column
    data = {
        "Gene1": np.random.rand(10),
        "Gene2": np.random.rand(10),
        "Group": ["A"] * 5 + ["B"] * 5,
    }
    df = pd.DataFrame(data)

    output_file = tmp_path / "pca_tidy.png"

    plotter = PCAPlot(theme="nature")
    fig = plotter.plot(
        data=df,
        hue="Group",
        transpose=False,  # Already Samples x Genes
        title="Test PCA Tidy",
        output=str(output_file),
    )

    assert output_file.exists()
    check_plot(fig)
