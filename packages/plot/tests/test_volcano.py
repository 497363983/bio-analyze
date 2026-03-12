from pathlib import Path

import pandas as pd
from bio_analyze_plot.plots.volcano import VolcanoPlot
from matplotlib.figure import Figure


def test_volcano_plot_generation():
    # Mock data
    data = pd.DataFrame(
        {
            "log2FoldChange": [2.5, -3.0, 0.5, 1.2],
            "pvalue": [0.001, 0.0001, 0.5, 0.04],
            "gene": ["A", "B", "C", "D"],
        }
    )

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "volcano.png"

    plotter = VolcanoPlot(theme="nature")
    fig = plotter.plot(data=data, x="log2FoldChange", y="pvalue", output=str(output_file))

    assert isinstance(fig, Figure)
    assert output_file.exists()
    assert output_file.stat().st_size > 0
