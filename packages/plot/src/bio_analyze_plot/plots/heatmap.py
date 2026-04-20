from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .base import BasePlot, save_plot


class HeatmapPlot(BasePlot):
    """
    Heatmap/Clustermap implementation.
    """

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        index_col: str | None = None,
        cluster_rows: bool = True,
        cluster_cols: bool = True,
        z_score: int | None = None,  # 0 表示行，1 表示列，None 表示不缩放
        cmap: str = "vlag",
        center: float = 0.0,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str | None = None,
        **kwargs: Any,
    ) -> Figure:
        """
        Plot heatmap with optional clustering.

        Args:
            data:
                DataFrame containing data.
            index_col:
                Column to use as index (labels). If None, uses existing index.
            cluster_rows:
                Whether to cluster rows.
            cluster_cols:
                Whether to cluster columns.
            z_score:
                0 (rows) or 1 (columns) for standardization. None to disable.
            cmap:
                Colormap name.
            center:
                Value at which to center the colormap.
            title:
                Chart title.
            xlabel:
                X-axis label.
            ylabel:
                Y-axis label.
            output:
                Path to save the chart.
            **kwargs:
                Other arguments passed to seaborn.clustermap.
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("heatmap")

        # 合并参数
        # 注意：这里我们优先使用 kwargs 中的参数，然后是函数参数，最后是主题参数
        # 但是由于函数参数有默认值，我们不能简单地 update。
        # 正确的逻辑是：如果 kwargs 中有，用 kwargs；如果没有，检查函数参数是否为非默认值（难判断）；
        # 实际上，通常主题参数作为默认值，函数参数作为覆盖。

        # 简化逻辑：
        # 1. 准备传递给 clustermap 的参数字典
        plot_kwargs = theme_params.copy()

        # 2. 更新显式传递的参数（非 None 或有特定值的）
        # 这里我们假设函数参数的默认值是我们想要的默认值，除非主题覆盖了它
        # 但通常函数参数优先级高于主题。

        # 让我们直接使用 kwargs 来覆盖 theme_params
        for k, v in kwargs.items():
            plot_kwargs[k] = v

        # 对于函数签名的参数，我们需要手动处理
        if "cmap" in theme_params and "cmap" not in kwargs:
            cmap = theme_params["cmap"]
        plot_kwargs["cmap"] = cmap

        if "center" in theme_params and "center" not in kwargs:
            center = theme_params["center"]
        plot_kwargs["center"] = center

        plot_kwargs["z_score"] = z_score
        plot_kwargs["row_cluster"] = cluster_rows
        plot_kwargs["col_cluster"] = cluster_cols

        df = data.copy()
        if index_col and index_col in df.columns:
            df = df.set_index(index_col)
            # Remove index name to avoid it being plotted as label if desired,
            # but usually we want it.

        # 仅选择数字列
        df_numeric = df.select_dtypes(include=["number"])

        # 处理非数值列作为索引或注释（如果需要），但在热图中通常只画数值
        # 如果 df 包含非数值列，clustermap 会报错或忽略。
        # 我们显式选择数值列以避免错误

        if df_numeric.empty:
            # 尝试转换
            try:
                df = df.astype(float)
                df_numeric = df
            except ValueError as e:
                raise ValueError("Heatmap requires numeric data.") from e

        # 创建 clustermap
        # 注意：clustermap 创建自己的 Figure，所以我们不使用 self.get_fig_ax()
        g = sns.clustermap(data=df_numeric, **plot_kwargs)

        if title:
            g.fig.suptitle(title, y=1.02)  # 稍微靠上

        if xlabel:
            g.ax_heatmap.set_xlabel(xlabel)
        if ylabel:
            g.ax_heatmap.set_ylabel(ylabel)

        return g.fig
