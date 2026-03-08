from __future__ import annotations

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from typing import Any

from .base import BasePlot, save_plot

class HeatmapPlot(BasePlot):
    """热图/聚类图实现。"""
    
    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        index_col: str | None = None,
        cluster_rows: bool = True,
        cluster_cols: bool = True,
        z_score: int | None = None, # 0 表示行，1 表示列，None 表示不缩放
        cmap: str = "vlag",
        center: float = 0.0,
        title: str = "Heatmap",
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str | None = None,
        **kwargs: Any
    ) -> Figure:
        """
        绘制带有可选聚类的热图。
        
        Args:
            data: 包含数据的 DataFrame。
            index_col: 用作索引（标签）的列。如果为 None，则使用现有索引。
            cluster_rows: 是否对行进行聚类。
            cluster_cols: 是否对列进行聚类。
            z_score: 0（行）或 1（列）进行标准化。None 表示禁用。
            cmap: 颜色映射名称。
            center: 颜色映射居中的值。
            title: 图表标题。
            xlabel: X轴标签。
            ylabel: Y轴标签。
            output: 保存图表的路径。
        """
        df = data.copy()
        if index_col and index_col in df.columns:
            df = df.set_index(index_col)
            
        # 仅选择数字列
        df = df.select_dtypes(include=['number'])

        # 创建 clustermap
        # 注意：clustermap 创建自己的 Figure，所以我们不使用 self.get_fig_ax()
        g = sns.clustermap(
            data=df,
            row_cluster=cluster_rows,
            col_cluster=cluster_cols,
            z_score=z_score,
            cmap=cmap,
            center=center,
            **kwargs
        )
        
        if title:
            g.fig.suptitle(title, y=1.02) # 稍微靠上
            
        if xlabel:
            g.ax_heatmap.set_xlabel(xlabel)
        if ylabel:
            g.ax_heatmap.set_ylabel(ylabel)
        
        return g.fig
