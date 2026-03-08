import matplotlib
matplotlib.use('Agg')
import pandas as pd
import pytest
from bio_plot.plots.heatmap import HeatmapPlot
from matplotlib.figure import Figure
from pathlib import Path

def test_heatmap_plot_generation():
    # Mock data
    data = pd.DataFrame({
        "gene": ["Gene1", "Gene2", "Gene3", "Gene4"],
        "Sample1": [1.2, 3.4, 0.5, 2.1],
        "Sample2": [1.1, 3.2, 0.6, 2.0],
        "Sample3": [4.5, 1.2, 3.3, 0.8],
        "Sample4": [4.6, 1.1, 3.2, 0.9]
    })
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "heatmap.png"
    
    plotter = HeatmapPlot(theme="nature")
    fig = plotter.plot(
        data=data,
        index_col="gene",
        cluster_rows=True,
        cluster_cols=True,
        z_score=0, # standardize rows
        output=str(output_file)
    )
    
    assert isinstance(fig, Figure)
    assert output_file.exists()
    assert output_file.stat().st_size > 0
