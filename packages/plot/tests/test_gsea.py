from pathlib import Path

import numpy as np
import pandas as pd
from bio_analyze_plot.plots.gsea import GSEAPlot
from matplotlib.figure import Figure


def test_gsea_plot_generation():
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

    data = pd.DataFrame({"rank": ranks, "running_es": es, "hit": hits, "metric": metric})

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Test 1: With metric and stats
    output_file = output_dir / "gsea_with_metric.png"
    plotter = GSEAPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        rank="rank",
        score="running_es",
        hit="hit",
        metric="metric",
        output=str(output_file),
        nes=1.5,
        pvalue=0.001,
        fdr=0.005,
    )

    assert isinstance(fig, Figure)
    assert output_file.exists()
    assert output_file.stat().st_size > 0

    # Test 2: Without metric
    output_file_no_metric = output_dir / "gsea_no_metric.png"
    fig2 = plotter.plot(data=data, rank="rank", score="running_es", hit="hit", output=str(output_file_no_metric))

    assert isinstance(fig2, Figure)
    assert output_file_no_metric.exists()
    assert output_file_no_metric.stat().st_size > 0

    # Test 3: No borders
    output_file_no_border = output_dir / "gsea_no_border.png"
    fig3 = plotter.plot(
        data=data,
        rank="rank",
        score="running_es",
        hit="hit",
        metric="metric",
        output=str(output_file_no_border),
        show_border=False,
    )

    assert isinstance(fig3, Figure)
    assert output_file_no_border.exists()
    assert output_file_no_border.stat().st_size > 0
