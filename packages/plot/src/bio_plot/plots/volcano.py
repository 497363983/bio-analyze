from __future__ import annotations

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure

from .base import BasePlot, save_plot

class VolcanoPlot(BasePlot):
    """火山图实现。"""
    
    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        x: str = "log2FoldChange",
        y: str = "pvalue",
        log_y: bool = True,
        fc_cutoff: float = 1.0,
        p_cutoff: float = 0.05,
        title: str = "Volcano Plot",
        xlabel: str | None = None,
        ylabel: str | None = None,
        output: str | None = None
    ) -> Figure:
        """
        绘制火山图。
        
        Args:
            data: 包含数据的 DataFrame。
            x: log2 fold change 的列名。
            y: p-value (或 adj. p-value) 的列名。
            log_y: 是否对 y 轴进行 -log10 转换。
            fc_cutoff: Fold change 截止值 (绝对值)。
            p_cutoff: P-value 截止值。
            title: 图表标题。
            xlabel: X轴标签。
            ylabel: Y轴标签。
            output: 保存图表的路径。
        """
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
            (df[x] <= -fc_cutoff) & (df[y] <= p_cutoff)
        ]
        choices = ["Up", "Down"]
        df["group"] = np.select(conditions, choices, default="Not Sig")
        
        # 调色板
        palette = {"Up": "#E41A1C", "Down": "#377EB8", "Not Sig": "grey"}
        
        fig, ax = self.get_fig_ax()
        
        sns.scatterplot(
            data=df,
            x=x,
            y=y_col,
            hue="group",
            palette=palette,
            alpha=0.7,
            edgecolor=None,
            s=15, # 标记大小
            ax=ax
        )
        
        # 添加截止线
        ax.axvline(x=fc_cutoff, color="grey", linestyle="--", linewidth=0.5)
        ax.axvline(x=-fc_cutoff, color="grey", linestyle="--", linewidth=0.5)
        if log_y:
            ax.axhline(y=-np.log10(p_cutoff), color="grey", linestyle="--", linewidth=0.5)
        else:
            ax.axhline(y=p_cutoff, color="grey", linestyle="--", linewidth=0.5)
            
        ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        
        # 将图例移到外侧或自定义
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        
        return fig
