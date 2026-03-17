import pandas as pd
from bio_analyze_plot.plots.bar import BarPlot
from matplotlib.figure import Figure


def test_bar_plot_generation(check_plot, tmp_path):
    # Mock data
    data = pd.DataFrame({"group": ["A", "B", "C"], "value": [10, 20, 15]})

    output_file = tmp_path / "bar.png"

    plotter = BarPlot(theme="default")
    fig = plotter.plot(data=data, x="group", y="value", output=str(output_file))

    assert output_file.exists()
    check_plot(fig)


def test_bar_plot_significance(check_plot, tmp_path):
    # Mock data with significant difference
    data = pd.DataFrame(
        {
            "group": ["A"] * 10 + ["B"] * 10,
            "value": [10 + i for i in range(10)] + [20 + i for i in range(10)],
        }
    )

    output_file = tmp_path / "bar_significance.png"

    plotter = BarPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="group",
        y="value",
        significance=[("A", "B")],
        test="t-test_ind",
        output=str(output_file),
    )

    assert output_file.exists()
    check_plot(fig)


def test_bar_plot_sd(check_plot, tmp_path):
    # Mock data with replicates for SD
    data = pd.DataFrame({"group": ["A", "A", "A", "B", "B", "B"], "value": [10, 12, 11, 20, 22, 21]})

    plotter = BarPlot(theme="nature")
    output_sd = tmp_path / "bar_sd.png"
    fig_sd = plotter.plot(data=data, x="group", y="value", error_bar_type="SD", output=str(output_sd))
    assert output_sd.exists()
    check_plot(fig_sd)


def test_bar_plot_se(check_plot, tmp_path):
    # Mock data with replicates for SE
    data = pd.DataFrame({"group": ["A", "A", "A", "B", "B", "B"], "value": [10, 12, 11, 20, 22, 21]})

    plotter = BarPlot(theme="nature")
    output_se = tmp_path / "bar_se.png"
    fig_se = plotter.plot(data=data, x="group", y="value", error_bar_type="SE", output=str(output_se))
    assert output_se.exists()
    check_plot(fig_se)


def test_bar_plot_custom_error_bars(check_plot, tmp_path):
    # Mock pre-aggregated data
    data = pd.DataFrame({"group": ["A", "B"], "mean": [10, 20], "min": [8, 18], "max": [12, 22]})

    output_file = tmp_path / "bar_custom.png"

    plotter = BarPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="group",
        y="mean",
        error_bar_max="max",
        error_bar_min="min",
        output=str(output_file),
    )

    assert output_file.exists()
    check_plot(fig)
