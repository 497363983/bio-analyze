from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .base import BasePlot, save_plot


class VolcanoPlot(BasePlot):
    """
    Volcano plot implementation.
    """

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        x: str = "log2FoldChange",
        y: str = "pvalue",
        log_y: bool = True,
        fc_cutoff: float = 1.0,
        p_cutoff: float = 0.05,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str | None = None,
        labels: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Figure:
        """
        Plot volcano plot.

        Args:
            data:
                DataFrame containing data.
            x:
                Column name for log2 fold change.
            y:
                Column name for p-value (or adj. p-value).
            log_y:
                Whether to apply -log10 transformation to y-axis.
            fc_cutoff:
                Fold change cutoff value (absolute).
            p_cutoff:
                P-value cutoff value.
            title:
                Chart title.
            xlabel:
                X-axis label.
            ylabel:
                Y-axis label.
            output:
                Path to save the chart.
            labels:
                Custom legend labels, dict with keys "up", "down", "ns".
                Defaults to `{"up": "Up", "down": "Down", "ns": "Not Sig"}`.
            **kwargs:
                Cutoff line style parameters, such as `color`, `linestyle`,
                and `linewidth`, plus any extra arguments forwarded to
                `seaborn.scatterplot`.
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("volcano")

        # 合并参数: kwargs > theme_params > defaults
        # 这里主要关注绘图样式参数，如 alpha, s, palette 等
        alpha = kwargs.get("alpha", theme_params.get("alpha", 0.7))
        s = kwargs.get("s", theme_params.get("s", 15))
        cutoff_line_kws = kwargs.get("cutoff_line_kws", theme_params.get("cutoff_line_kws", {}))

        # 默认截止线样式
        default_line_kws = {"color": "grey", "linestyle": "--", "linewidth": 0.5}
        cutoff_line_kws = {**default_line_kws, **cutoff_line_kws}
        default_labels = {"up": "Up", "down": "Down", "ns": "Not Sig"}
        # 优先级：参数 > 主题 > 默认
        theme_labels = theme_params.get("labels", {})
        user_labels = labels or {}
        final_labels = {**default_labels, **theme_labels, **user_labels}

        # 调色板
        # 默认调色板使用 final_labels 中的值作为键
        default_palette = {final_labels["up"]: "#E41A1C", final_labels["down"]: "#377EB8", final_labels["ns"]: "grey"}
        palette = kwargs.get("palette", theme_params.get("palette", default_palette))

        df = data.copy()

        # 如果需要，计算 -log10(pvalue)
        if log_y:
            y_col = f"-log10({y})"
            df[y_col] = -np.log10(df[y])
        else:
            y_col = y

        # 定义分组
        conditions = [
            (df[x] >= fc_cutoff) & (df[y] <= p_cutoff),
            (df[x] <= -fc_cutoff) & (df[y] <= p_cutoff),
        ]
        choices = [final_labels["up"], final_labels["down"]]
        df["group"] = np.select(conditions, choices, default=final_labels["ns"])

        # 调色板
        # palette = {"Up": "#E41A1C", "Down": "#377EB8", "Not Sig": "grey"}

        fig, ax = self.get_fig_ax()

        # 过滤 kwargs，排除已显式使用的参数和非绘图参数
        plot_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["palette", "alpha", "s", "cutoff_line_kws", "labels"]
        }

        sns.scatterplot(
            data=df,
            x=x,
            y=y_col,
            hue="group",
            palette=palette,
            alpha=alpha,
            edgecolor=None,
            s=s,  # 标记大小
            ax=ax,
            **plot_kwargs,
        )

        # 添加截止线
        ax.axvline(x=fc_cutoff, **cutoff_line_kws)
        ax.axvline(x=-fc_cutoff, **cutoff_line_kws)
        if log_y:
            ax.axhline(y=-np.log10(p_cutoff), **cutoff_line_kws)
        else:
            ax.axhline(y=p_cutoff, **cutoff_line_kws)

        if title:
            ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        # 将图例移到外侧或自定义
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

        return fig
