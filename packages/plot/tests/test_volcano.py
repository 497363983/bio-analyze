import pandas as pd
from bio_analyze_plot.plots.volcano import VolcanoPlot
from matplotlib.figure import Figure


def test_volcano_plot_generation(check_plot, tmp_path):
    # Mock data
    data = pd.DataFrame(
        {
            "log2FoldChange": [2.5, -3.0, 0.5, 1.2],
            "pvalue": [0.001, 0.0001, 0.5, 0.04],
            "gene": ["A", "B", "C", "D"],
        }
    )

    output_file = tmp_path / "volcano.png"

    plotter = VolcanoPlot(theme="nature")
    fig = plotter.plot(data=data, x="log2FoldChange", y="pvalue", output=str(output_file))

    assert output_file.exists()
    assert output_file.stat().st_size > 0
    check_plot(fig)
