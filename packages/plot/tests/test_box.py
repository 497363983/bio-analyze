import pandas as pd
from bio_analyze_plot.plots.box import BoxPlot
from matplotlib.figure import Figure


def test_box_plot_generation(check_plot, tmp_path):
    # Mock data
    data = pd.DataFrame(
        {"group": ["A"] * 10 + ["B"] * 10, "value": [10 + i for i in range(10)] + [20 + i for i in range(10)]}
    )

    output_file = tmp_path / "box.png"

    plotter = BoxPlot(theme="default")
    fig = plotter.plot(data=data, x="group", y="value", output=str(output_file))

    assert output_file.exists()
    check_plot(fig)


def test_box_plot_significance(check_plot, tmp_path):
    # Mock data with significant difference
    data = pd.DataFrame(
        {
            "group": ["A"] * 10 + ["B"] * 10,
            "value": [10 + i for i in range(10)] + [20 + i for i in range(10)],
        }
    )

    output_file = tmp_path / "box_significance.png"

    plotter = BoxPlot(theme="nature")
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


def test_box_plot_swarm(check_plot, tmp_path):
    # Mock data with significant difference
    data = pd.DataFrame(
        {
            "group": ["A"] * 10 + ["B"] * 10,
            "value": [10 + i for i in range(10)] + [20 + i for i in range(10)],
        }
    )

    output_file = tmp_path / "box_swarm.png"

    plotter = BoxPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="group",
        y="value",
        add_swarm=True,
        output=str(output_file),
    )

    assert output_file.exists()
    check_plot(fig)
