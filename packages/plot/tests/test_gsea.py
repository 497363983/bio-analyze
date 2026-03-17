import numpy as np
import pandas as pd
import pytest
from bio_analyze_plot.plots.gsea import GSEAPlot
from matplotlib.figure import Figure


@pytest.fixture
def gsea_data():
    # Mock data for GSEA
    # 100 genes
    ranks = np.arange(100)
    # Simple running ES: goes up then down
    es = np.concatenate([np.linspace(0, 0.5, 30), np.linspace(0.5, -0.2, 40), np.linspace(-0.2, 0, 30)])
    # Hits: sparse
    hits = np.zeros(100)
    hits[[10, 20, 25, 30, 80, 90]] = 1
    # Metric: decreasing
    metric = np.linspace(5, -5, 100)

    return pd.DataFrame({"rank": ranks, "running_es": es, "hit": hits, "metric": metric})


def test_gsea_with_metric(gsea_data, check_plot, tmp_path):
    output_file = tmp_path / "gsea_with_metric.png"
    plotter = GSEAPlot(theme="nature")
    fig = plotter.plot(
        data=gsea_data,
        rank="rank",
        score="running_es",
        hit="hit",
        metric="metric",
        output=str(output_file),
        nes=1.5,
        pvalue=0.001,
        fdr=0.005,
    )
    assert output_file.exists()
    check_plot(fig)


def test_gsea_no_metric(gsea_data, check_plot, tmp_path):
    output_file = tmp_path / "gsea_no_metric.png"
    plotter = GSEAPlot(theme="nature")
    fig = plotter.plot(
        data=gsea_data,
        rank="rank",
        score="running_es",
        hit="hit",
        output=str(output_file)
    )
    assert output_file.exists()
    check_plot(fig)


def test_gsea_no_border(gsea_data, check_plot, tmp_path):
    output_file = tmp_path / "gsea_no_border.png"
    plotter = GSEAPlot(theme="nature")
    fig = plotter.plot(
        data=gsea_data,
        rank="rank",
        score="running_es",
        hit="hit",
        metric="metric",
        output=str(output_file),
        show_border=False,
    )
    assert output_file.exists()
    check_plot(fig)
