from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from .base import BasePlot, save_plot


class ChromosomePlot(BasePlot):
    """染色体 Reads 覆盖度分布图（Track 风格）。"""

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        chrom_col: str = "chrom",
        pos_col: str = "pos",
        pos_counts_col: str = "counts_pos",
        neg_counts_col: str = "counts_neg",
        title: str = "Reads Coverage Distribution on Chromosomes",
        output: str | None = None,
        max_chroms: int = 30,
        bin_size: int = 100000,
        color_pos: str | None = None,
        color_neg: str | None = None,
        **kwargs: Any,
    ) -> Figure:
        """
        绘制 Reads 在染色体上的覆盖度分布图（区分正负链）。

        Args:
            data: 包含 bin 统计数据的 DataFrame。
                  必需列: chrom, pos (bin start), counts_pos, counts_neg
            chrom_col: 染色体列名。
            pos_col: 位置列名（bin 起始位）。
            pos_counts_col: 正链 Reads 计数列名。
            neg_counts_col: 负链 Reads 计数列名。
            title: 图表标题。
            output: 保存路径。
            max_chroms: 最多显示的染色体数量（按长度或名称排序后）。
            bin_size: Bin 大小（用于 X 轴单位换算或标注）。
            color_pos: 正链颜色。
            color_neg: 负链颜色。
            label_pos: 正链图例标签。
            label_neg: 负链图例标签。
            zero_line_kws: 零线的样式参数。
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("chromosome")

        # 合并参数
        color_pos = color_pos or kwargs.get("color_pos", theme_params.get("color_pos", "#4DBBD5"))
        color_neg = color_neg or kwargs.get("color_neg", theme_params.get("color_neg", "#E64B35"))
        label_pos = kwargs.get("label_pos", theme_params.get("label_pos", "Strand +"))
        label_neg = kwargs.get("label_neg", theme_params.get("label_neg", "Strand -"))
        zero_line_kws = kwargs.get("zero_line_kws", theme_params.get("zero_line_kws", {}))

        # 默认零线样式
        default_zero_kws = {"color": "gray", "linewidth": 0.5, "alpha": 0.3}
        zero_line_kws = {**default_zero_kws, **zero_line_kws}

        # 1. 准备数据
        # 过滤染色体：只保留主要的
        # 简单的自然排序逻辑
        def natural_key(string):
            import re

            return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", string)]

        all_chroms = sorted(data[chrom_col].unique(), key=lambda s: natural_key(str(s)))

        # 如果染色体太多，尝试过滤掉 scaffold (含有非数字/XYMT的复杂名称)
        # 或者只取前 max_chroms
        display_chroms = all_chroms[:max_chroms]

        # 过滤数据
        plot_data = data[data[chrom_col].isin(display_chroms)].copy()

        # 计算 Log2(Depth + 1) 用于绘图高度
        # 假设 counts 是 reads count。
        # log2(count + 1)
        plot_data["log_pos"] = np.log2(plot_data[pos_counts_col] + 1)
        plot_data["log_neg"] = np.log2(plot_data[neg_counts_col] + 1)

        # 2. 绘图设置
        n_chroms = len(display_chroms)
        # 动态计算高度：每个染色体一行
        fig_height = max(6, n_chroms * 0.8)
        fig, axes = plt.subplots(
            nrows=n_chroms, ncols=1, figsize=(12, fig_height), sharex=True, gridspec_kw={"hspace": 0.1}
        )

        if n_chroms == 1:
            axes = [axes]

        # 统一 Y 轴范围（为了美观，或者每行独立？）
        # 独立可能更好，因为染色体间表达量差异巨大。
        # 但为了对比，统一也可以。这里采用每行独立自动缩放，但保持对称。

        # 颜色
        # color_pos = color_pos or kwargs.get("color_pos", "#4DBBD5")  # 青色 (Nature/Science 风格)
        # color_neg = color_neg or kwargs.get("color_neg", "#E64B35")  # 红色

        for i, chrom in enumerate(display_chroms):
            ax = axes[i]
            chrom_data = plot_data[plot_data[chrom_col] == chrom]

            x = chrom_data[pos_col]
            y_p = chrom_data["log_pos"]
            y_n = chrom_data["log_neg"]  # 负链也画在上方还是下方？参考图是分上下。

            # 绘制正链（上方）
            ax.fill_between(x, 0, y_p, color=color_pos, alpha=0.8, label="Strand +" if i == 0 else "")

            # 绘制负链（下方，取负值）
            ax.fill_between(x, 0, -y_n, color=color_neg, alpha=0.8, label="Strand -" if i == 0 else "")

            # 设置 Y 轴标签（在右侧或左侧显示染色体名）
            # ax.set_ylabel(chrom, rotation=0, ha="right", va="center", fontsize=10)

            # 使用 twinx 在右侧显示染色体名称
            ax_right = ax.twinx()
            ax_right.set_ylabel(chrom, rotation=0, ha="left", va="center", fontsize=10)
            ax_right.set_yticks([])  # 移除右侧刻度
            ax_right.spines["top"].set_visible(False)
            ax_right.spines["bottom"].set_visible(False)
            ax_right.spines["right"].set_visible(False)
            ax_right.spines["left"].set_visible(False)

            # 恢复左侧 Y 轴刻度 (Depth log2)
            # 为了避免刻度过于密集，只显示最大值和最小值（负值）
            max_y = max(y_p.max(), 0.1) if not y_p.empty else 1
            min_y = min(-y_n.max(), -0.1) if not y_n.empty else -1

            # 设置 Y 轴范围，稍微留点空间
            limit = max(abs(max_y), abs(min_y)) * 1.1
            ax.set_ylim(-limit, limit)

            # 设置刻度：显示正负最大值和 0
            # 格式化刻度标签，去掉小数
            tick_val = int(limit * 0.8)
            # 如果 tick_val 为 0，确保至少显示 -1, 0, 1 (或者仅 0)
            if tick_val == 0:
                tick_val = 1

            ax.set_yticks([-tick_val, 0, tick_val])
            # 负链显示负号
            ax.set_yticklabels([f"-{tick_val}", "0", f"{tick_val}"], fontsize=8)
            ax.tick_params(axis="y", length=2, pad=2)  # 调整刻度线长度和间距

            # 添加一条淡淡的零线
            ax.axhline(0, color="gray", linewidth=0.5, alpha=0.3)

            # 设置背景透明或白色
            ax.patch.set_alpha(0)

            # 移除不需要的边框
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            # 保留左侧边框以显示坐标轴
            ax.spines["left"].set_visible(True)

            if i < n_chroms - 1:
                ax.spines["bottom"].set_visible(False)
                ax.tick_params(bottom=False)

        # 设置总标题和 X 轴标签
        fig.suptitle(title, y=0.99)  # 稍微调高
        axes[-1].set_xlabel("Position (bp)")

        # 添加左侧总 Y 轴标签 (Depth)
        # 可以在整个图的左侧添加一个大的 label
        fig.text(0.02, 0.5, "Depth (log2)", va="center", rotation="vertical", fontsize=12)

        # 添加图例（在第一个子图或 fig 级别）
        # 创建自定义图例句柄
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor=color_pos, label="Strand +"),
            Patch(facecolor=color_neg, label="Strand -"),
        ]
        fig.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(0.95, 0.98))

        # fig.tight_layout(rect=[0, 0, 1, 0.98])  # 留出标题空间
        # 由于我们手动调整了 axes，tight_layout 可能会报错，特别是当 fig.axes 很多时。
        # 尝试使用 subplots_adjust
        fig.subplots_adjust(top=0.95, bottom=0.05, left=0.1, right=0.9, hspace=0.1)

        return fig
