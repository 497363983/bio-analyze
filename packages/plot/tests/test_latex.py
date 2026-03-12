from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from bio_analyze_plot.plots.line import LinePlot
from matplotlib.figure import Figure

matplotlib.use("Agg")


def test_latex_support():
    # ?? LaTeX ????
    data = pd.DataFrame({"x": np.linspace(0, 10, 20), "y": np.sin(np.linspace(0, 10, 20))})

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "latex_test.png"

    plotter = LinePlot(theme="nature")
    fig = plotter.plot(
        data=data,
        x="x",
        y="y",
        # ?? LaTeX ??????????
        title=r"Sin Wave: $y = \sin(x)$",
        xlabel=r"Time ($t$)",
        ylabel=r"Amplitude ($\alpha$)",
        output=str(output_file),
    )

    # ???????????????????????
    # ???????????
    assert isinstance(fig, Figure)
    assert output_file.exists()
