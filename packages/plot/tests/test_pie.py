import pandas as pd
from bio_analyze_plot.plots.pie import PiePlot
import matplotlib.pyplot as plt

def test_pie_plot(check_plot, tmp_path):
    # Create sample data
    data = pd.DataFrame({"Category": ["A", "B", "C", "D"], "Value": [10, 20, 30, 40]})

    output_path = tmp_path / "pie_chart.png"

    plotter = PiePlot()
    fig = plotter.plot(data=data, x="Category", y="Value", title="Test Pie Chart", output=str(output_path))

    assert output_path.exists()
    assert isinstance(fig, plt.Figure)
    assert output_path.stat().st_size > 0
    check_plot(fig)


def test_pie_plot_explode(check_plot, tmp_path):
    data = pd.DataFrame({"Category": ["A", "B", "C"], "Value": [30, 20, 50], "Explode": [0.1, 0, 0]})

    output_path = tmp_path / "pie_chart_explode.png"

    plotter = PiePlot()
    fig = plotter.plot(
        data=data, x="Category", y="Value", explode="Explode", title="Exploded Pie Chart", output=str(output_path)
    )

    assert output_path.exists()
    check_plot(fig)


def test_pie_plot_explode_list(check_plot, tmp_path):
    data = pd.DataFrame({"Category": ["A", "B", "C"], "Value": [30, 20, 50]})

    output_path = tmp_path / "pie_chart_explode_list.png"

    plotter = PiePlot()
    fig = plotter.plot(
        data=data,
        x="Category",
        y="Value",
        explode=[0.1, 0, 0],
        title="Exploded Pie Chart List",
        output=str(output_path),
    )

    assert output_path.exists()
    check_plot(fig)
