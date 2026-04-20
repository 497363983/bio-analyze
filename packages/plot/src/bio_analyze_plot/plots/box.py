from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from statannotations.Annotator import Annotator

from .base import BasePlot, save_plot


class BoxPlot(BasePlot):
    """
    Box plot implementation.
    """

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        hue: str | None = None,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str | None = None,
        significance: list[tuple[str, str]] | None = None,
        test: str = "t-test_ind",
        text_format: str = "star",
        add_swarm: bool = False,
        swarm_color: str = ".25",
        swarm_size: float = 3,
        **kwargs: Any,
    ) -> Figure:
        """
        Plot box chart.

        Args:
            data:
                DataFrame containing data.
            x:
                Column name for x-axis.
            y:
                Column name for y-axis.
            hue:
                Column name for grouping.
            title:
                Chart title.
            xlabel:
                X-axis label.
            ylabel:
                Y-axis label.
            output:
                Path to save the chart.
            significance:
                List of pairs for significance testing.
            test:
                Statistical test method.
            text_format:
                Significance annotation format.
            add_swarm:
                Whether to overlay swarmplot.
            swarm_color:
                Color of swarm points.
            swarm_size:
                Size of swarm points.
            **kwargs:
                Other arguments passed to seaborn.boxplot.
        """
        theme_params = self.get_chart_specific_params("box")

        if "palette" not in kwargs and "palette" in theme_params:
            kwargs["palette"] = theme_params["palette"]

        fig, ax = self.get_fig_ax()

        sns.boxplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)

        if add_swarm:
            # 如果有 hue，需要设置 dodge=True 以便散点与箱线图对齐
            dodge = bool(hue)
            sns.swarmplot(
                data=data,
                x=x,
                y=y,
                hue=hue,
                dodge=dodge,
                color=swarm_color,
                size=swarm_size,
                ax=ax,
            )
            # 移除 swarmplot 可能产生的重复图例
            # 通常 boxplot 会生成图例，swarmplot 也会。
            # 这里我们保留现有的图例处理方式，不做额外复杂的图例清理，
            # 除非发现明显问题。

        if significance:
            annotator = Annotator(
                ax,
                pairs=significance,
                data=data,
                x=x,
                y=y,
                hue=hue,
                order=kwargs.get("order"),
                hue_order=kwargs.get("hue_order"),
            )
            annotator.configure(test=test, text_format=text_format, loc="inside")
            annotator.apply_and_annotate()

        if title:
            ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        return fig
