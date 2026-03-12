from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .base import BasePlot, save_plot


class LinePlot(BasePlot):
    """折线图实现。"""

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
        **kwargs: Any,
    ) -> Figure:
        """
        绘制折线图。

        Args:
            data: 包含数据的 DataFrame。
            x: x 轴的列名。
            y: y 轴的列名。
            hue: 分组列名。
            title: 图表标题。
            xlabel: X轴标签。
            ylabel: Y轴标签。
            output: 保存图表的路径。
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("line")

        # 合并参数: kwargs > theme_params
        # 例如 palette, linewidth, markersize 等
        if "palette" not in kwargs and "palette" in theme_params:
            kwargs["palette"] = theme_params["palette"]

        for k, v in theme_params.items():
            if k not in kwargs:
                kwargs[k] = v

        fig, ax = self.get_fig_ax()
        sns.lineplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)
        if title:
            ax.set_title(title)
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        return fig
