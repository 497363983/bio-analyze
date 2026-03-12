from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from bio_analyze_plot.plots.pca import PCAPlot
from matplotlib.figure import Figure

matplotlib.use("Agg")


def test_pca_clustering():
    # Create dummy expression data: 100 genes x 9 samples
    # 3 groups structure
    np.random.seed(42)
    data = np.random.rand(100, 9)
    data[:, 0:3] += 3  # Cluster 1
    data[:, 3:6] -= 3  # Cluster 2
    # Cluster 3 is random around 0

    df = pd.DataFrame(data, columns=[f"S{i}" for i in range(1, 10)])

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "pca_cluster.png"

    plotter = PCAPlot(theme="nature")
    fig = plotter.plot(
        data=df,
        transpose=True,
        title="PCA with Clustering",
        cluster=True,
        n_clusters=3,
        output=str(output_file),
    )

    assert isinstance(fig, Figure)
    assert output_file.exists()
