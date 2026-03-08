import pandas as pd
import pytest
from bio_plot.plots.line import LinePlot
from matplotlib.figure import Figure

from pathlib import Path

def test_line_plot_generation():
    # Mock data
    data = pd.DataFrame({
        "time": [1, 2, 3, 1, 2, 3],
        "value": [10, 20, 15, 5, 8, 12],
        "group": ["A", "A", "A", "B", "B", "B"]
    })
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "line.png"
    
    plotter = LinePlot(theme="science")
    fig = plotter.plot(
        data=data,
        x="time",
        y="value",
        hue="group",
        output=str(output_file)
    )
    
    assert isinstance(fig, Figure)
    assert output_file.exists()
