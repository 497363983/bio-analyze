import matplotlib

matplotlib.use("Agg")
import numpy as np
import pandas as pd
from bio_analyze_plot.plots.bar import BarPlot
from bio_analyze_plot.plots.chromosome import ChromosomeDistributionPlot
from bio_analyze_plot.plots.pca import PCAPlot
from bio_analyze_plot.plots.volcano import VolcanoPlot


def test_volcano_custom_labels():
    df = pd.DataFrame({"log2FoldChange": [2, -2, 0.5, 3], "pvalue": [0.001, 0.001, 0.5, 0.0001]})

    plotter = VolcanoPlot()
    # Test with custom labels
    custom_labels = {"up": "Upregulated", "down": "Downregulated", "ns": "Insignificant"}
    fig = plotter.plot(
        df,
        x="log2FoldChange",
        y="pvalue",
        labels=custom_labels,
        palette={"Upregulated": "red", "Downregulated": "green", "Insignificant": "gray"},
        cutoff_line_kws={"color": "black", "linestyle": "-"},
    )
    assert fig is not None


def test_pca_custom_style():
    # Mock data
    df = pd.DataFrame(np.random.rand(10, 5), columns=["A", "B", "C", "D", "E"])
    df["Group"] = ["G1"] * 5 + ["G2"] * 5

    plotter = PCAPlot()
    fig = plotter.plot(
        df,
        transpose=True,  # default
        hue="Group",  # Group is in index or column? Transpose=True means df is genes x samples.
        # Wait, PCAPlot doc says: transpose: usually expression matrix is gene x sample. PCA needs sample x gene.
        # If transpose=True, input is gene x sample. It transposes to sample x gene.
        # Hue should be a list or Series matching columns (samples).
        # Let's use transpose=False for simpler test: sample x gene.
    )
    # Re-do test with correct data shape

    # Sample x Gene
    df2 = pd.DataFrame(np.random.rand(10, 5), columns=[f"Gene{i}" for i in range(5)])
    df2["Group"] = ["G1"] * 5 + ["G2"] * 5

    fig = plotter.plot(
        df2, transpose=False, hue="Group", cluster=True, ellipse_kws={"alpha": 0.5, "facecolor": "yellow"}
    )
    assert fig is not None


def test_bar_custom_colors():
    df = pd.DataFrame({"x": ["A", "B"], "y": [10, 20], "err_max": [11, 21], "err_min": [9, 19]})

    plotter = BarPlot()
    fig = plotter.plot(
        df, "x", "y", error_bar_max="err_max", error_bar_min="err_min", err_color="blue", cap_color="red"
    )
    assert fig is not None


def test_chromosome_custom_labels():
    df = pd.DataFrame({"chrom": ["chr1", "chr1"], "pos": [100, 200], "counts_pos": [10, 20], "counts_neg": [5, 15]})

    plotter = ChromosomeDistributionPlot()
    fig = plotter.plot(
        df,
        label_pos="Positive Strand",
        label_neg="Negative Strand",
        color_pos="pink",
        color_neg="purple",
        zero_line_kws={"color": "black", "linewidth": 1},
    )
    assert fig is not None
