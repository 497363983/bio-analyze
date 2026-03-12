from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import gridspec
from matplotlib.figure import Figure

from .base import BasePlot, save_plot


class GSEAPlot(BasePlot):
    """GSEA 富集图实现。"""

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        rank: str = "rank",
        score: str = "running_es",
        hit: str = "hit",
        metric: str | None = None,
        title: str | None = None,
        output: str | None = None,
        color: str = "#4DAF4A",  # ES 线的默认绿色
        hit_color: str = "black",
        nes: float | None = None,
        pvalue: float | None = None,
        fdr: float | None = None,
        show_border: bool = True,
        **kwargs: Any,
    ) -> Figure:
        """
        绘制 GSEA 富集图。

        Args:
            data: 包含 GSEA 结果的 DataFrame。
            rank: 排名列名（x 轴）。
            score: 运行富集分数列名（y 轴顶部）。
            hit: 命中状态列名（布尔值或 0/1）。
            metric: 排名指标列名（y 轴底部）。可选。
            title: 图表标题。
            output: 输出文件路径。
            color: 富集分数线的颜色。
            hit_color: 命中垂直线的颜色。
            nes: 标准化富集评分（用于注释）。
            pvalue: P 值（用于注释）。
            fdr: FDR/调整后的 P 值（用于注释）。
            show_border: 是否显示子图的顶部和右侧边框。默认为 True。
        """
        # 获取主题参数
        theme_params = self.get_chart_specific_params("gsea")
        color = kwargs.get("color", theme_params.get("color", color))
        hit_color = kwargs.get("hit_color", theme_params.get("hit_color", hit_color))
        show_border = kwargs.get("show_border", theme_params.get("show_border", show_border))

        # 确定底部面板是否有指标数据
        has_metric = metric is not None and metric in data.columns

        # 定义布局
        if has_metric:
            # 顶部 (ES)，中间 (命中 + 颜色条)，底部 (指标)
            height_ratios = [2.5, 0.5, 2]
            figsize = (6, 6)
        else:
            height_ratios = [3, 0.5]
            figsize = (6, 4)

        fig = plt.figure(figsize=figsize)
        gs = gridspec.GridSpec(len(height_ratios), 1, height_ratios=height_ratios, hspace=0.05)

        # 通用 x 轴限制
        x_min, x_max = data[rank].min(), data[rank].max()

        # --- 1. 富集评分 (顶部面板) ---
        ax0 = fig.add_subplot(gs[0])

        # 绘制 ES 线
        # 如果需要可以使用渐变线，但标准是纯色。
        # 用户图片有渐变线，如果存在指标，让我们尝试将其与指标颜色图匹配。
        # 但目前简单的纯色更安全。让我们使用用户提供的颜色。
        sns.lineplot(data=data, x=rank, y=score, color=color, linewidth=2, ax=ax0)

        # 零线
        ax0.axhline(0, color="black", linestyle="--", linewidth=1)

        # 注释 (NES, Pvalue, FDR)
        stats_text = []
        if nes is not None:
            stats_text.append(f"NES: {nes:.2f}")
        if pvalue is not None:
            pval_str = f"{pvalue:.2e}" if pvalue < 0.001 else f"{pvalue:.3f}"
            stats_text.append(f"Pvalue: {pval_str}")
        if fdr is not None:
            fdr_str = f"{fdr:.2e}" if fdr < 0.001 else f"{fdr:.3f}"
            stats_text.append(f"FDR: {fdr_str}")

        if stats_text:
            # 添加文本到右上角
            text_str = "\n".join(stats_text)
            ax0.text(
                0.95,
                0.95,
                text_str,
                transform=ax0.transAxes,
                ha="right",
                va="top",
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec="none"),
            )

        ax0.set_ylabel("Running Enrichment Score", fontsize=12)
        if title:
            ax0.set_title(title, fontsize=14, pad=10)
        ax0.set_xlim(x_min, x_max)
        ax0.set_xticklabels([])
        ax0.set_xlabel("")
        ax0.grid(False)

        # 配置边框
        ax0.spines["top"].set_visible(show_border)
        ax0.spines["right"].set_visible(show_border)

        # --- 2. 命中 & 颜色条 (中间面板) ---
        ax1 = fig.add_subplot(gs[1], sharex=ax0)

        # A. 颜色条背景 (热图条)
        # 我们需要值来进行着色。如果存在指标，则使用它。
        # 如果不存在，我们无法真正制作颜色条，只能显示命中。
        if has_metric:
            # 为 imshow 创建网格
            # 我们需要一行颜色对应于指标值
            # 指标值通常按排名排序？
            # 假设数据已按排名排序用于绘图
            metric_vals = data.sort_values(rank)[metric].values
            # 重塑为 imshow (1, N)
            metric_img = metric_vals.reshape(1, -1)

            # 使用 RdBu_r 颜色图 (红色表示高/正，蓝色表示低/负)
            # 使用 vmin/vmax 对称将颜色图以 0 为中心
            max_abs = max(abs(np.min(metric_vals)), abs(np.max(metric_vals)))

            ax1.imshow(
                metric_img, aspect="auto", cmap="RdBu_r", vmin=-max_abs, vmax=max_abs, extent=[x_min, x_max, 0, 1]
            )

        # B. 命中 (垂直线)
        # 过滤命中
        hits = data[data[hit].astype(bool)]
        ax1.vlines(hits[rank], ymin=0, ymax=1, colors=hit_color, linewidth=0.8)

        ax1.set_ylabel("")
        ax1.set_yticks([])
        ax1.set_xlabel("")
        ax1.set_xticklabels([])
        ax1.set_xlim(x_min, x_max)

        # 移除脊柱以获得更清晰的外观
        for spine in ax1.spines.values():
            spine.set_visible(True)  # 保留边框？用户图片有边框。

        ax1.spines["top"].set_visible(show_border)
        ax1.spines["right"].set_visible(show_border)

        # --- 3. 指标 (底部面板) ---
        if has_metric:
            ax2 = fig.add_subplot(gs[2], sharex=ax0)

            metric_data = data.sort_values(rank)
            x_vals = metric_data[rank]
            y_vals = metric_data[metric]

            # 填充正值 (红色)
            ax2.fill_between(
                x_vals,
                y_vals,
                0,
                where=(y_vals >= 0),
                color="#E41A1C",  # Red
                alpha=0.6,
                interpolate=True,
            )

            # 填充负值 (蓝色)
            ax2.fill_between(
                x_vals,
                y_vals,
                0,
                where=(y_vals < 0),
                color="#377EB8",  # Blue
                alpha=0.6,
                interpolate=True,
            )

            # 零线
            ax2.axhline(0, color="black", linestyle="--", linewidth=1)

            ax2.set_ylabel("Ranked List Metric", fontsize=10)
            ax2.set_xlabel("Rank in Ordered Dataset", fontsize=12)
            ax2.set_xlim(x_min, x_max)

            ax2.spines["top"].set_visible(show_border)
            ax2.spines["right"].set_visible(show_border)

            # 调整 y 轴限制为对称或紧凑
            # 标准 GSEA 通常清晰显示指标

        else:
            # 如果没有指标，向中间面板添加标签
            ax1.set_xlabel("Rank in Ordered Dataset", fontsize=12)

        return fig
