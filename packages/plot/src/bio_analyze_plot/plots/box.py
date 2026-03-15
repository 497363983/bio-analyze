from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from statannotations.Annotator import Annotator

from .base import BasePlot, save_plot


class BoxPlot(BasePlot):
    """
    zh: 箱线图实现。
    en: Box plot implementation.
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
        zh: 绘制箱线图。
        en: Plot box chart.

        Args:
            data:
                zh: 包含数据的 DataFrame。
                en: DataFrame containing data.
            x:
                zh: x 轴的列名。
                en: Column name for x-axis.
            y:
                zh: y 轴的列名。
                en: Column name for y-axis.
            hue:
                zh: 分组列名。
                en: Column name for grouping.
            title:
                zh: 图表标题。
                en: Chart title.
            xlabel:
                zh: X轴标签。
                en: X-axis label.
            ylabel:
                zh: Y轴标签。
                en: Y-axis label.
            output:
                zh: 保存图表的路径。
                en: Path to save the chart.
            significance:
                zh: 要进行显著性检验的配对列表。
                en: List of pairs for significance testing.
            test:
                zh: 统计检验方法。
                en: Statistical test method.
            text_format:
                zh: 显著性标记格式。
                en: Significance annotation format.
            add_swarm:
                zh: 是否叠加散点图 (swarmplot)。
                en: Whether to overlay swarmplot.
            swarm_color:
                zh: 散点颜色。
                en: Color of swarm points.
            swarm_size:
                zh: 散点大小。
                en: Size of swarm points.
            **kwargs:
                zh: 其他传递给 seaborn.boxplot 的参数。
                en: Other arguments passed to seaborn.boxplot.
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
