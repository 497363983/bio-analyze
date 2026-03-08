from __future__ import annotations

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from typing import Any

from .core import BasePlotter, save_plot

class BasicPlotter(BasePlotter):
    
    @save_plot()
    def line(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        hue: str | None = None,
        title: str = "Line Plot",
        output: str | None = None,
        **kwargs: Any
    ) -> Figure:
        fig, ax = self.get_fig_ax()
        sns.lineplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)
        ax.set_title(title)
        return fig

    @save_plot()
    def bar(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        hue: str | None = None,
        title: str = "Bar Plot",
        output: str | None = None,
        **kwargs: Any
    ) -> Figure:
        fig, ax = self.get_fig_ax()
        sns.barplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)
        ax.set_title(title)
        return fig
