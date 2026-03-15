from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from scipy.interpolate import make_interp_spline

from .base import BasePlot, save_plot


class LinePlot(BasePlot):
    """
    zh: 折线图实现。
    en: Line plot implementation.
    """

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
        error_bar_ci: float | int = 95,
        error_bar_max: str | None = None,
        error_bar_min: str | None = None,
        error_bar_capsize: float = 3.0,  # Capsize in points for lineplot
        err_color: str | None = None,
        cap_color: str | None = None,
        markers: bool | str | list | dict | None = None,
        dashes: bool | list | dict | None = True,
        smooth: bool = False,
        smooth_points: int = 300,
        **kwargs: Any,
    ) -> Figure:
        """
        zh: 绘制折线图。
        en: Plot line chart.

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
            error_bar_type:
                zh: 误差棒类型 (SD, SE, CI)。
                en: Error bar type (SD, SE, CI).
            error_bar_ci:
                zh: 当类型为 CI 时的置信区间大小 (默认 95)。
                en: Confidence interval size when type is CI (default 95).
            error_bar_max:
                zh: 误差棒上限的列名 (暂不支持手动绘制，仅占位)。
                en: Column name for error bar upper bound (placeholder, manual drawing not supported yet).
            error_bar_min:
                zh: 误差棒下限的列名 (暂不支持手动绘制，仅占位)。
                en: Column name for error bar lower bound (placeholder, manual drawing not supported yet).
            error_bar_capsize:
                zh: 误差棒的横线宽度 (单位: points)。
                en: Width of error bar caps (unit: points).
            err_color:
                zh: 误差棒颜色。
                en: Error bar color.
            cap_color:
                zh: 误差棒横线颜色 (对于 lineplot，通常与 err_color 一致)。
                en: Error bar cap color (usually same as err_color for lineplot).
            markers:
                zh: 是否显示数据点标记，或指定标记样式。
                en: Whether to show data point markers, or specify marker style.
            dashes:
                zh: 是否显示虚线，或指定虚线样式。
                en: Whether to show dashes, or specify dash style.
            smooth:
                zh: 是否启用平滑曲线拟合。
                en: Whether to enable smooth curve fitting.
            smooth_points:
                zh: 平滑曲线的插值点数。
                en: Number of interpolation points for smooth curve.
            **kwargs:
                zh: 其他传递给 seaborn.lineplot 的参数。
                en: Other arguments passed to seaborn.lineplot.
        """
        # 获取主题特定参数
        theme_params = self.get_chart_specific_params("line")

        # 合并参数: kwargs > theme_params
        if "palette" not in kwargs and "palette" in theme_params:
            kwargs["palette"] = theme_params["palette"]

        for k, v in theme_params.items():
            if k not in kwargs:
                kwargs[k] = v

        # 处理 markers 和 dashes
        if "markers" not in kwargs and markers is not None:
            kwargs["markers"] = markers
        if "dashes" not in kwargs and dashes is not None:
            kwargs["dashes"] = dashes

        if "style" not in kwargs and hue is not None:
            kwargs["style"] = hue

        # 确定 seaborn 的 errorbar 参数
        errorbar_arg = None
        if error_bar_type:
            eb_type = error_bar_type.upper()
            if eb_type == "SD":
                errorbar_arg = "sd"
            elif eb_type == "SE":
                errorbar_arg = "se"
            elif eb_type == "CI":
                ci_val = error_bar_ci
                if isinstance(ci_val, float) and ci_val < 1.0:
                    ci_val = ci_val * 100
                errorbar_arg = ("ci", ci_val)

        # 如果用户没有指定 error_bar_type，但在 kwargs 中可能有 errorbar (来自之前的实现或用户习惯)
        if errorbar_arg is None and "errorbar" in kwargs:
            errorbar_arg = kwargs.pop("errorbar")

        # 强制使用 bars 样式以显示 cap
        err_style = "bars"

        # 构造 err_kws
        err_kws = kwargs.get("err_kws", {}).copy()

        # 设置 capsize
        if error_bar_capsize is not None:
            err_kws["capsize"] = error_bar_capsize

        # 设置颜色
        if err_color:
            err_kws["ecolor"] = err_color  # ax.errorbar 使用 ecolor

        kwargs["err_kws"] = err_kws

        fig, ax = self.get_fig_ax()

        if smooth:
            # 生成平滑数据
            smooth_list = []

            def get_smooth_series(sub_df, group_val=None):
                # 聚合以获取唯一 x (均值)
                if sub_df.empty:
                    return sub_df
                agg = sub_df.groupby(x)[y].mean().sort_index().reset_index()
                x_vals = agg[x].values
                y_vals = agg[y].values

                # 至少需要4个点进行三次样条插值
                if len(x_vals) < 4:
                    return agg

                try:
                    # 使用 B-spline 插值
                    spl = make_interp_spline(x_vals, y_vals, k=3)
                    x_new = np.linspace(x_vals.min(), x_vals.max(), smooth_points)
                    y_new = spl(x_new)

                    new_df = pd.DataFrame({x: x_new, y: y_new})
                    if group_val is not None and hue:
                        new_df[hue] = group_val
                    return new_df
                except Exception:
                    # 如果插值失败，回退到聚合后的数据
                    return agg

            if hue:
                # 获取 hue 顺序
                hue_order = kwargs.get("hue_order")
                if hue_order is None:
                    hue_order = sorted(data[hue].unique())

                for g in hue_order:
                    sub = data[data[hue] == g]
                    smooth_list.append(get_smooth_series(sub, g))
            else:
                smooth_list.append(get_smooth_series(data))

            if smooth_list:
                smoothed_data = pd.concat(smooth_list, ignore_index=True)
            else:
                smoothed_data = data  # Fallback

            # 如果需要绘制误差棒，先用原始数据绘制误差棒和标记（不画线）
            if errorbar_arg is not None:
                # 复制 kwargs 并强制不画线
                bg_kwargs = kwargs.copy()
                bg_kwargs["linewidth"] = 0  # 显式设置线宽为0以完全隐藏连接线
                bg_kwargs["dashes"] = False  # 禁用虚线逻辑，避免 matplotlib 报错
                bg_kwargs["legend"] = False  # 不显示图例，由平滑线显示

                # 移除 linestyle 设置，避免干扰
                if "linestyle" in bg_kwargs:
                    del bg_kwargs["linestyle"]

                # 确保 markers 显示（如果用户没显式关掉）
                # 如果 markers 是 None (默认)，我们可能希望显示 markers 以标示原始点位置
                # 因为线已经平滑了，点如果不显示，用户看不到真实数据位置
                if markers is None:
                    bg_kwargs["markers"] = True

                sns.lineplot(
                    data=data, x=x, y=y, hue=hue, ax=ax, errorbar=errorbar_arg, err_style=err_style, **bg_kwargs
                )

                # 然后绘制平滑线（无误差棒，无标记）
                fg_kwargs = kwargs.copy()
                fg_kwargs["marker"] = None
                fg_kwargs["markers"] = False

                sns.lineplot(data=smoothed_data, x=x, y=y, hue=hue, ax=ax, errorbar=None, **fg_kwargs)
            else:
                # 无误差棒，直接绘制平滑线
                sns.lineplot(data=smoothed_data, x=x, y=y, hue=hue, ax=ax, errorbar=None, **kwargs)
        else:
            # 正常绘制
            sns.lineplot(data=data, x=x, y=y, hue=hue, ax=ax, errorbar=errorbar_arg, err_style=err_style, **kwargs)

        if title:
            ax.set_title(title)
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        return fig
