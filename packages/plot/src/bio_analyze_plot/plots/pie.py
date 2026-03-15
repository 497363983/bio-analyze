from __future__ import annotations

from typing import Any

import pandas as pd
from matplotlib.figure import Figure

from .base import BasePlot, save_plot


class PiePlot(BasePlot):
    """
    zh: 饼图实现。
    en: Pie chart implementation.
    """

    @save_plot
    def plot(
        self,
        data: pd.DataFrame,
        x: str,  # labels
        y: str,  # values
        title: str | None = None,
        autopct: str = "%1.1f%%",
        startangle: float = 90,
        explode: str | list[float] | None = None,
        shadow: bool = False,
        colors: list[str] | None = None,
        output: str | None = None,
        **kwargs: Any,
    ) -> Figure:
        """
        zh: 绘制饼图。
        en: Plot pie chart.

        Args:
            data:
                zh: 包含数据的 DataFrame。
                en: DataFrame containing data.
            x:
                zh: 标签列名 (Categorical)。
                en: Column name for labels (Categorical).
            y:
                zh: 数值列名 (Numerical)。
                en: Column name for values (Numerical).
            title:
                zh: 图表标题。
                en: Chart title.
            autopct:
                zh: 百分比显示格式，例如 '%1.1f%%'。
                en: Percentage format string, e.g., '%1.1f%%'.
            startangle:
                zh: 起始角度。
                en: Starting angle.
            explode:
                zh: 突出显示的切片。可以是列名（布尔值或数值），也可以是列表。
                en: Slices to explode. Can be column name (boolean or numeric) or list.
            shadow:
                zh: 是否显示阴影。
                en: Whether to show shadow.
            colors:
                zh: 颜色列表。
                en: List of colors.
            output:
                zh: 保存图表的路径。
                en: Path to save the chart.
            **kwargs:
                zh: 其他传递给 matplotlib.pyplot.pie 的参数。
                en: Other arguments passed to matplotlib.pyplot.pie.
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("pie")

        # 调色板/颜色
        if colors is None:
            if "colors" in theme_params:
                colors = theme_params["colors"]
            elif "palette" in theme_params:
                # 如果主题提供了调色板名称，尝试使用 seaborn 调色板生成颜色
                import seaborn as sns

                palette_name = theme_params["palette"]
                n_colors = len(data)
                colors = sns.color_palette(palette_name, n_colors)

        fig, ax = self.get_fig_ax()

        labels = data[x]
        values = data[y]

        explode_vals = None
        if explode:
            if isinstance(explode, str) and explode in data.columns:
                explode_vals = data[explode].tolist()
            elif isinstance(explode, (list, tuple)):
                explode_vals = explode

        # 确保 explode_vals 长度匹配
        if explode_vals and len(explode_vals) != len(values):
            # 如果长度不匹配，可能需要填充或截断，或者警告
            # 这里简单起见，如果不匹配则设为 None
            explode_vals = None

        ax.pie(
            values,
            explode=explode_vals,
            labels=labels,
            colors=colors,
            autopct=autopct,
            shadow=shadow,
            startangle=startangle,
            **kwargs,
        )

        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
        if title:
            ax.set_title(title)

        return fig
