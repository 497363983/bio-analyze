from pathlib import Path
import pytest
from bio_analyze_plot.plots.tree import TreePlot

@pytest.fixture
def sample_tree():
    return Path(__file__).parent / "data" / "tree_cli.nwk"

def test_tree_plot_default(sample_tree, check_plot):
    plotter = TreePlot(theme="default")
    
    fig = plotter.plot(
        data=sample_tree,
        format="newick",
        show_confidence=True
    )
    
    assert fig is not None
    check_plot(fig)

def test_tree_plot_no_confidence(sample_tree, check_plot):
    plotter = TreePlot(theme="default")
    
    fig = plotter.plot(
        data=sample_tree,
        format="newick",
        show_confidence=False
    )
    
    assert fig is not None
    check_plot(fig)

def test_tree_plot_custom_style(sample_tree, check_plot):
    plotter = TreePlot(theme="science")
    
    fig = plotter.plot(
        data=sample_tree,
        format="newick",
        layout="rectangular",
        show_confidence=True,
        branch_thickness=2.5,
        font_size=14,
        figsize=(10, 8)
    )
    
    assert fig is not None
    check_plot(fig)

def test_tree_plot_circular(sample_tree, check_plot):
    plotter = TreePlot(theme="default")
    
    fig = plotter.plot(
        data=sample_tree,
        format="newick",
        layout="circular",
        show_confidence=True
    )
    
    assert fig is not None
    check_plot(fig)


def test_tree_plot_label_params(sample_tree):
    plotter = TreePlot(theme="default")

    fig = plotter.plot(
        data=sample_tree,
        format="newick",
        layout="rectangular",
        show_confidence=True,
        label_offset_scale=0.1,
        label_bbox_alpha=0.3
    )

    assert fig is not None
    label_map = {t.get_text().strip(): t for t in fig.axes[0].texts if t.get_text().strip()}
    assert "QWO78770.1" in label_map
    bbox = label_map["QWO78770.1"].get_bbox_patch()
    assert bbox is not None
    assert bbox.get_alpha() == 0.3
