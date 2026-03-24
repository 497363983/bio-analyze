import json
from pathlib import Path
import pytest
from matplotlib.colors import to_hex
from bio_analyze_plot.plots.msa import MsaPlot

@pytest.fixture
def sample_msa():
    return Path(__file__).parent / "data" / "aligned_cli.fasta"

def test_msa_plot(sample_msa, check_plot):
    plotter = MsaPlot(theme="nature")
    
    fig = plotter.plot(
        data=sample_msa,
        seq_type="nt",
        show_logo=True
    )
    
    assert fig is not None
    check_plot(fig)


def test_msa_plot_wrap_by_bases_per_line(sample_msa, check_plot):
    plotter = MsaPlot(theme="nature")

    fig = plotter.plot(
        data=sample_msa,
        seq_type="aa",
        show_logo=False,
        bases_per_line=60
    )

    assert fig is not None
    ax = fig.axes[0]
    assert ax.get_xlim() == (-0.5, 59.5)
    assert len(ax.get_yticklabels()) > 8
    check_plot(fig)


def test_msa_plot_custom_base_colors(sample_msa, check_plot):
    plotter = MsaPlot(theme="nature")
    fig = plotter.plot(
        data=sample_msa,
        seq_type="aa",
        show_logo=False,
        bases_per_line=60,
        base_colors={"A": "#000000", "-": "#f8f8f8"}
    )
    ax = fig.axes[0]
    first_color = to_hex(ax.images[0].cmap.colors[0]).lower()
    assert first_color == "#000000"
    check_plot(fig)


def test_msa_plot_theme_chart_specific_params(sample_msa, check_plot, tmp_path):
    theme_file = tmp_path / "msa_theme.json"
    theme_file.write_text(
        json.dumps(
            {
                "name": "msa_theme",
                "chart_specific_params": {
                    "msa": {
                        "seq_type": "aa",
                        "show_logo": False,
                        "bases_per_line": 60,
                        "font_size": 9,
                        "base_colors": {"A": "#111111", "-": "#f8f8f8"}
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    plotter = MsaPlot(theme=str(theme_file))
    fig = plotter.plot(data=sample_msa)
    ax = fig.axes[0]
    assert ax.get_xlim() == (-0.5, 59.5)
    first_color = to_hex(ax.images[0].cmap.colors[0]).lower()
    assert first_color == "#111111"
    check_plot(fig)
