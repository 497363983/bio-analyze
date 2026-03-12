import matplotlib

matplotlib.use("Agg")
from pathlib import Path

import pandas as pd
from bio_analyze_plot.plots.bar import BarPlot
from matplotlib.figure import Figure


def test_bar_plot_generation():
    # Mock data
    data = pd.DataFrame({"group": ["A", "B", "C"], "value": [10, 20, 15]})

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "bar.png"

    plotter = BarPlot(theme="default")
    fig = plotter.plot(data=data, x="group", y="value", output=str(output_file))

    assert isinstance(fig, Figure)
    assert output_file.exists()


def test_bar_plot_significance():
    # Mock data with significant difference
    data = pd.DataFrame(
        {
            "group": ["A"] * 10 + ["B"] * 10,
            "value": [10 + i for i in range(10)] + [20 + i for i in range(10)],
        }
    )

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "bar_significance.png"

    plotter = BarPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="group",
        y="value",
        significance=[("A", "B")],
        test="t-test_ind",
        output=str(output_file),
    )

    assert isinstance(fig, Figure)
    assert output_file.exists()


def test_bar_plot_with_error_bars():
    # Mock data with replicates for SD/SE
    data = pd.DataFrame({"group": ["A", "A", "A", "B", "B", "B"], "value": [10, 12, 11, 20, 22, 21]})

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Test SD
    plotter = BarPlot(theme="nature")
    output_sd = output_dir / "bar_sd.png"
    fig_sd = plotter.plot(data=data, x="group", y="value", error_bar_type="SD", output=str(output_sd))
    assert isinstance(fig_sd, Figure)
    assert output_sd.exists()

    # Test SE
    output_se = output_dir / "bar_se.png"
    fig_se = plotter.plot(data=data, x="group", y="value", error_bar_type="SE", output=str(output_se))
    assert output_se.exists()


def test_bar_plot_custom_error_bars():
    # Mock pre-aggregated data
    data = pd.DataFrame({"group": ["A", "B"], "mean": [10, 20], "min": [8, 18], "max": [12, 22]})

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "bar_custom.png"

    plotter = BarPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="group",
        y="mean",
        error_bar_max="max",
        error_bar_min="min",
        output=str(output_file),
    )

    assert isinstance(fig, Figure)
    assert output_file.exists()
