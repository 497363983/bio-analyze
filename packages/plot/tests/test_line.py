import pandas as pd
from bio_analyze_plot.plots.line import LinePlot
from matplotlib.figure import Figure


def test_line_plot_generation(check_plot, tmp_path):
    # Mock data
    data = pd.DataFrame(
        {
            "time": [1, 2, 3, 1, 2, 3],
            "value": [10, 20, 15, 5, 8, 12],
            "group": ["A", "A", "A", "B", "B", "B"],
        }
    )

    output_file = tmp_path / "line.png"

    plotter = LinePlot(theme="science")
    fig = plotter.plot(data=data, x="time", y="value", hue="group", output=str(output_file))

    assert output_file.exists()
    check_plot(fig)
