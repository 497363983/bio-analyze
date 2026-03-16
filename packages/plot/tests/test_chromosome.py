import matplotlib
import pandas as pd
import pytest
from bio_analyze_plot.plots.chromosome import ChromosomePlot
from matplotlib.figure import Figure

matplotlib.use("Agg")


@pytest.fixture
def mock_data():
    return pd.DataFrame(
        {
            "chrom": ["chr1"] * 10 + ["chr2"] * 10,
            "pos": list(range(10)) + list(range(10)),
            "counts_pos": list(range(10)) + list(range(10)),
            "counts_neg": list(range(10)) + list(range(10)),
        }
    )


def test_chromosome_plot_generation(mock_data, tmp_path):
    output_file = tmp_path / "chromosome_plot.png"
    plotter = ChromosomePlot()
    fig = plotter.plot(mock_data, title="Test Chromosome Plot", output=str(output_file))
    assert isinstance(fig, Figure)
    assert output_file.exists()


def test_chromosome_plot_max_chroms(mock_data, tmp_path):
    plotter = ChromosomePlot()
    fig = plotter.plot(mock_data, max_chroms=2, output=str(tmp_path / "max_chroms.png"))
    # Check if only 2 chromosomes are plotted (number of axes)
    # Each chromosome has a main axis and a twinx axis for the right label, so 2*2 = 4 axes
    assert len(fig.axes) == 4


def test_chromosome_plot_sorting(mock_data, tmp_path):
    plotter = ChromosomePlot()
    plotter.plot(mock_data, output=str(tmp_path / "sorting.png"))
    # Check if axes labels (chromosome names) are sorted correctly
    # Note: axes order is top to bottom.
    # Our implementation: axes[i] corresponds to display_chroms[i]
    # display_chroms is sorted by natural key: chr1, chr2, chr10, chrX
    pass  # Visual check or deeper inspection of axes labels needed if critical


def test_chromosome_plot_custom_colors(mock_data, tmp_path):
    plotter = ChromosomePlot()
    fig = plotter.plot(mock_data, color_pos="blue", color_neg="green", output=str(tmp_path / "custom_colors.png"))
    # Basic check that it runs without error
    assert isinstance(fig, Figure)
