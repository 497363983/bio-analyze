from __future__ import annotations

from typing import Any

import matplotlib.transforms as transforms
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse

from .base import BasePlot, save_plot


def confidence_ellipse(x, y, ax, n_std=2.0, facecolor="none", **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2, facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D().rotate_deg(45).scale(scale_x, scale_y).translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


class ScatterPlot(BasePlot):
    """
    zh: 散点图实现。
    en: Scatter plot implementation.
    """

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        hue: str | None = None,
        style: str | None = None,
        size: str | None = None,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str | None = None,
        add_ellipse: bool = False,
        ellipse_std: float = 2.0,
        **kwargs: Any,
    ) -> Figure:
        """
        zh: 绘制散点图。
        en: Plot scatter chart.

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
            style:
                zh: 样式分组列名。
                en: Column name for style grouping.
            size:
                zh: 大小分组列名。
                en: Column name for size grouping.
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
            add_ellipse:
                zh: 是否为每个分组绘制置信椭圆。
                en: Whether to draw confidence ellipses for each group.
            ellipse_std:
                zh: 椭圆的标准差倍数。
                en: Number of standard deviations for ellipse.
            **kwargs:
                zh: 其他传递给 seaborn.scatterplot 的参数。
                en: Other arguments passed to seaborn.scatterplot.
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("scatter")

        # 合并参数: kwargs > theme_params
        if "palette" not in kwargs and "palette" in theme_params:
            kwargs["palette"] = theme_params["palette"]

        # s (size) 是常见的 seaborn 参数
        if "s" not in kwargs and "s" in theme_params:
            kwargs["s"] = theme_params["s"]

        for k, v in theme_params.items():
            if k not in kwargs:
                kwargs[k] = v

        fig, ax = self.get_fig_ax()

        # 椭圆绘制逻辑
        if add_ellipse and hue:
            # 椭圆样式参数
            ellipse_kws = kwargs.pop("ellipse_kws", theme_params.get("ellipse_kws", {})).copy()
            if "alpha" not in ellipse_kws:
                ellipse_kws["alpha"] = 0.1

            # 确保有 palette
            palette = kwargs.get("palette")
            if palette is None:
                unique_groups = data[hue].unique()
                n_colors = len(unique_groups)
                colors = sns.color_palette(n_colors=n_colors)
                palette = dict(zip(unique_groups, colors))
                # 更新 kwargs 以便 scatterplot 使用相同的 palette
                kwargs["palette"] = palette

            unique_groups = data[hue].unique()
            for group in unique_groups:
                group_data = data[data[hue] == group]
                # 至少需要 3 个点来绘制有意义的椭圆
                if len(group_data) < 3:
                    continue

                # 获取颜色
                color = palette[group] if isinstance(palette, dict) else None

                # 准备填充样式
                final_ellipse_kws = ellipse_kws.copy()
                if "facecolor" not in final_ellipse_kws:
                    final_ellipse_kws["facecolor"] = color

                # 绘制填充椭圆
                confidence_ellipse(
                    group_data[x], group_data[y], ax, n_std=ellipse_std, edgecolor="none", zorder=0, **final_ellipse_kws
                )

                # 绘制轮廓
                final_outline_kws = ellipse_kws.copy()
                if "alpha" in final_outline_kws:
                    del final_outline_kws["alpha"]
                if "facecolor" in final_outline_kws:
                    del final_outline_kws["facecolor"]

                confidence_ellipse(
                    group_data[x],
                    group_data[y],
                    ax,
                    n_std=ellipse_std,
                    edgecolor=color,
                    facecolor="none",
                    linestyle="--",
                    linewidth=1,
                    zorder=0,
                )

        # 绘制散点
        sns.scatterplot(data=data, x=x, y=y, hue=hue, style=style, size=size, ax=ax, **kwargs)

        if title:
            ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        return fig
