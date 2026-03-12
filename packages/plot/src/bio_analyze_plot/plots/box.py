from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from statannotations.Annotator import Annotator

from .base import BasePlot, save_plot


class BoxPlot(BasePlot):
    """箱线图实现。"""

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
        绘制箱线图。

        Args:
            data: 包含数据的 DataFrame。
            x: x 轴的列名。
            y: y 轴的列名。
            hue: 分组列名。
            title: 图表标题。
            xlabel: X轴标签。
            ylabel: Y轴标签。
            output: 保存图表的路径。
            significance: 要进行显著性检验的配对列表。
            test: 统计检验方法。
            text_format: 显著性标记格式。
            add_swarm: 是否叠加散点图 (swarmplot)。
            swarm_color: 散点颜色。
            swarm_size: 散点大小。
        """
        theme_params = self.get_chart_specific_params("box")

        if "palette" not in kwargs and "palette" in theme_params:
            kwargs["palette"] = theme_params["palette"]

        fig, ax = self.get_fig_ax()

        sns.boxplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)

        if add_swarm:
            # 如果有 hue，需要设置 dodge=True 以便散点与箱线图对齐
            dodge = True if hue else False
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
