import inspect
import json

import matplotlib.pyplot as plt
from bio_analyze_plot.plots import (
    BarPlot,
    BasePlot,
    BoxPlot,
    ChromosomePlot,
    GSEAPlot,
    HeatmapPlot,
    LinePlot,
    MsaPlot,
    PCAPlot,
    PiePlot,
    ScatterPlot,
    TreePlot,
    VolcanoPlot,
)
from bio_analyze_plot.plots.base import save_plot


PLOT_KEY_CLASS_PAIRS = [
    ("bar", BarPlot),
    ("box", BoxPlot),
    ("chromosome", ChromosomePlot),
    ("gsea", GSEAPlot),
    ("heatmap", HeatmapPlot),
    ("line", LinePlot),
    ("msa", MsaPlot),
    ("pca", PCAPlot),
    ("pie", PiePlot),
    ("scatter", ScatterPlot),
    ("tree", TreePlot),
    ("volcano", VolcanoPlot),
]


class DummyPlot(BasePlot):
    @save_plot
    def plot(self, data, **kwargs):
        fig, ax = self.get_fig_ax()
        ax.plot([0, 1], [0, 1])
        return fig


def test_all_plot_types_support_chart_specific_params(tmp_path):
    theme_path = tmp_path / "all_plots_theme.json"
    chart_specific_params = {key: {"_marker": key} for key, _ in PLOT_KEY_CLASS_PAIRS}
    theme_path.write_text(
        json.dumps({"name": "all_plots_theme", "chart_specific_params": chart_specific_params}),
        encoding="utf-8",
    )

    for key, plot_cls in PLOT_KEY_CLASS_PAIRS:
        plotter = plot_cls(theme=str(theme_path))
        params = plotter.get_chart_specific_params(key)
        assert params["_marker"] == key


def test_all_plot_types_read_chart_specific_params_in_plot_method():
    for key, plot_cls in PLOT_KEY_CLASS_PAIRS:
        source = inspect.getsource(plot_cls.plot)
        assert f'get_chart_specific_params("{key}")' in source


def test_chart_specific_rc_params_applied_and_restored(tmp_path):
    theme_path = tmp_path / "dummy_theme.json"
    theme_path.write_text(
        json.dumps(
            {
                "name": "dummy_theme",
                "chart_specific_params": {
                    "dummy": {"foo": 1, "rc_params": {"lines.linewidth": 4.2}}
                },
            }
        ),
        encoding="utf-8",
    )

    original_linewidth = plt.rcParams["lines.linewidth"]
    plotter = DummyPlot(theme=str(theme_path))
    params = plotter.get_chart_specific_params("dummy")
    rc_params = plotter.get_chart_rc_params("dummy")

    assert "rc_params" not in params
    assert params["foo"] == 1
    assert rc_params["lines.linewidth"] == 4.2

    fig = plotter.plot(data=None)
    drawn_linewidth = fig.axes[0].lines[0].get_linewidth()
    assert drawn_linewidth == 4.2
    assert plt.rcParams["lines.linewidth"] == original_linewidth
