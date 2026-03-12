import matplotlib

matplotlib.use("Agg")
from pathlib import Path

import pandas as pd
from bio_analyze_plot.plots.box import BoxPlot
from matplotlib.figure import Figure


def test_box_plot_generation():
    # Mock data
    data = pd.DataFrame(
        {"group": ["A"] * 10 + ["B"] * 10, "value": [10 + i for i in range(10)] + [20 + i for i in range(10)]}
    )

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "box.png"

    plotter = BoxPlot(theme="default")
    fig = plotter.plot(data=data, x="group", y="value", output=str(output_file))

    assert isinstance(fig, Figure)
    assert output_file.exists()


def test_box_plot_significance():
    # Mock data with significant difference
    data = pd.DataFrame(
        {
            "group": ["A"] * 10 + ["B"] * 10,
            "value": [10 + i for i in range(10)] + [20 + i for i in range(10)],
        }
    )

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "box_significance.png"

    plotter = BoxPlot(theme="nature")
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


def test_box_plot_swarm():
    # Mock data with significant difference
    data = pd.DataFrame(
        {
            "group": ["A"] * 10 + ["B"] * 10,
            "value": [10 + i for i in range(10)] + [20 + i for i in range(10)],
        }
    )

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "box_swarm.png"

    plotter = BoxPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="group",
        y="value",
        add_swarm=True,
        output=str(output_file),
    )

    assert isinstance(fig, Figure)
    assert output_file.exists()
