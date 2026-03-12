from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from statannotations.Annotator import Annotator

from .base import BasePlot, save_plot


class BarPlot(BasePlot):
    """柱状图实现。"""

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
        error_bar_type: str | None = None,  # SD, SE, CI
        error_bar_ci: float | int = 95,  # Confidence interval (e.g. 95 or 0.95)
        error_bar_max: str | None = None,  # Column name for upper bound
        error_bar_min: str | None = None,  # Column name for lower bound
        error_bar_capsize: float = 0.1,  # Error bar capsize
        significance: list[tuple[str, str]] | None = None,  # List of pairs to compare e.g. [("Control", "Treated")]
        test: str = "t-test_ind",  # t-test_ind, t-test_welch, t-test_paired, Mann-Whitney, Wilcoxon, Kruskal
        text_format: str = "star",  # star, full, simple, pvalue
        err_color: str | None = None,
        cap_color: str | None = None,
        **kwargs: Any,
    ) -> Figure:
        """
        绘制带有误差棒的柱状图。

        Args:
            data: 包含数据的 DataFrame。
            x: x 轴的列名。
            y: y 轴的列名。
            hue: 分组列名。
            title: 图表标题。
            xlabel: X轴标签。
            ylabel: Y轴标签。
            output: 保存图表的路径。
            error_bar_type: 误差棒类型 (SD, SE, CI)。如果提供了 max/min 则忽略。
            error_bar_ci: 当类型为 CI 时的置信区间大小 (默认 95)。
            error_bar_max: 误差棒上限的列名。
            error_bar_min: 误差棒下限的列名。
            error_bar_capsize: 误差棒的横线宽度。
            significance: 要进行显著性检验的配对列表。例如 [("A", "B"), ("C", "D")]。
                          如果是分组柱状图 (有 hue)，则格式为 [((x1, hue1), (x2, hue2)), ...]。
            test: 统计检验方法。支持 't-test_ind', 't-test_welch', 't-test_paired', 'Mann-Whitney', 'Wilcoxon', 'Kruskal'。
            text_format: 显著性标记格式 ('star', 'full', 'simple', 'pvalue')。
            err_color: 误差棒颜色。
            cap_color: 误差棒横线颜色。
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("bar")

        # 合并参数
        err_color = err_color or kwargs.get("err_color", theme_params.get("err_color", "black"))
        cap_color = cap_color or kwargs.get("cap_color", theme_params.get("cap_color", "black"))
        # 调色板
        if "palette" not in kwargs and "palette" in theme_params:
            kwargs["palette"] = theme_params["palette"]

        fig, ax = self.get_fig_ax()

        # 确定 seaborn 的 errorbar 参数
        errorbar_arg = None

        if error_bar_max and error_bar_min:
            # 自定义误差棒处理：首先禁用 seaborn 的误差棒
            errorbar_arg = None
        elif error_bar_type:
            # 映射用户类型到 seaborn errorbar
            eb_type = error_bar_type.upper()
            if eb_type == "SD":
                errorbar_arg = "sd"
            elif eb_type == "SE":
                errorbar_arg = "se"
            elif eb_type == "CI":
                # 处理置信区间值：如果是 0.95 转换为 95
                ci_val = error_bar_ci
                if isinstance(ci_val, float) and ci_val < 1.0:
                    ci_val = ci_val * 100
                errorbar_arg = ("ci", ci_val)
            else:
                errorbar_arg = None
        else:
            # 未指定误差棒
            errorbar_arg = None

        # 绘制主柱状图
        # 注意：如果未指定，seaborn 默认为 errorbar=('ci', 95)。
        # 所以如果我们不想要它，必须显式传递 None。
        # 准备绘图参数，默认添加 capsize 以显示误差棒的横线
        plot_kwargs = kwargs.copy()
        if "capsize" not in plot_kwargs:
            plot_kwargs["capsize"] = error_bar_capsize

        # 设置 errcolor 和 errwidth (seaborn < 0.12) 或使用 line_kws (seaborn > 0.12)
        # 避免使用已弃用的 errcolor
        if "err_kws" not in plot_kwargs:
            plot_kwargs["err_kws"] = {"color": err_color, "linewidth": plot_kwargs.get("errwidth")}
        else:
            if "color" not in plot_kwargs["err_kws"]:
                plot_kwargs["err_kws"]["color"] = err_color

        # 移除 errwidth 以避免警告（如果已移至 err_kws）
        if "errwidth" in plot_kwargs:
            del plot_kwargs["errwidth"]

        plot_obj = sns.barplot(data=data, x=x, y=y, hue=hue, ax=ax, errorbar=errorbar_arg, **plot_kwargs)

        # 添加显著性标记
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

        # 处理自定义误差棒（提供了 max/min）
        if error_bar_max and error_bar_min:
            # 确保数据与绘图顺序对齐/排序
            # Seaborn 默认对分类轴进行排序（按字典顺序或按提供的顺序）
            # 如果存在 hue，则是嵌套的。

            # 这很复杂，因为我们需要将条形与数据行匹配。
            # 假设：数据已预聚合（每个条形一行）。

            # 获取轴上的条形
            bars = ax.patches

            # 如果我们有 hue，seaborn 通常会先绘制第一个 hue 级别的所有条形，然后是第二个，依此类推。
            # 或者交错？
            # 实际上，seaborn < 0.12 与 > 0.12 的行为可能不同。
            # 在现代 seaborn（对象接口）中更清晰。但我们使用的是函数接口。

            # 策略：迭代 patches 并尝试找到对应的数据。
            # 更好的策略：根据 x 和 hue 手动计算坐标。

            # 让我们简化：
            # 1. 按顺序获取唯一的 x 值（seaborn 顺序）
            # 2. 按顺序获取唯一的 hue 值
            # 3. 迭代 x 和 hue 以找到数据行

            x_vals = sorted(data[x].unique())  # 如果未给出顺序，Seaborn 默认排序
            if kwargs.get("order"):
                x_vals = kwargs["order"]

            hue_vals = [None]
            if hue:
                hue_vals = sorted(data[hue].unique())
                if kwargs.get("hue_order"):
                    hue_vals = kwargs["hue_order"]

            # 计算条形宽度和偏移量
            n_hues = len(hue_vals)
            # 默认宽度为 0.8
            total_width = 0.8
            bar_width = total_width / n_hues

            # 迭代并绘制误差棒
            # 注意：此实现假设 x 轴为数值或映射到 0, 1, 2... 的分类

            for i, x_val in enumerate(x_vals):
                for j, hue_val in enumerate(hue_vals):
                    # 查找数据行
                    if hue:
                        row = data[(data[x] == x_val) & (data[hue] == hue_val)]
                    else:
                        row = data[data[x] == x_val]

                    if row.empty:
                        continue

                    # 假设每组一行用于预计算的误差
                    row = row.iloc[0]

                    y_val = row[y]
                    y_min = row[error_bar_min]
                    y_max = row[error_bar_max]

                    # 计算 x 坐标
                    # 基础 x 是 i
                    # 偏移量取决于 hue 索引 j
                    # 组中心是 i
                    # 组起始是 i - total_width/2
                    # 条形 j 起始于：start + j * bar_width
                    # 条形 j 中心是：start + j * bar_width + bar_width/2

                    x_center = i - total_width / 2 + j * bar_width + bar_width / 2

                    # 绘制误差棒
                    ax.errorbar(
                        x=x_center,
                        y=y_val,
                        yerr=[[y_val - y_min], [y_max - y_val]],
                        fmt="none",
                        color=err_color,
                        capsize=0,
                    )

                    # 手动绘制 Caps 以确保与 Seaborn 的 capsize 单位（数据坐标）一致
                    # ax.errorbar 的 capsize 是 points 单位，而这里我们需要数据坐标单位
                    half_cap = error_bar_capsize / 2
                    ax.plot(
                        [x_center - half_cap, x_center + half_cap],
                        [y_min, y_min],
                        color=cap_color,
                        linewidth=1.5,
                    )
                    ax.plot(
                        [x_center - half_cap, x_center + half_cap],
                        [y_max, y_max],
                        color=cap_color,
                        linewidth=1.5,
                    )

        if title:
            ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        return fig
