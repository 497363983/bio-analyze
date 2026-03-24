from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..theme import THEMES, load_custom_theme, set_theme

F = TypeVar("F", bound=Callable[..., Any])


def save_plot(func: F) -> F:
    """
    zh: 保存图表到文件的装饰器。
    en: Decorator to save plot to file.

    Args:
        func (F):
            zh: 绘图函数
            en: Plotting function

    Returns:
        F:
            zh: 装饰后的函数
            en: Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        output = kwargs.pop("output", None)
        plotter = args[0] if args else None
        chart_type = plotter.infer_chart_type() if isinstance(plotter, BasePlot) else None
        rc_params = plotter.get_chart_rc_params(chart_type) if chart_type and isinstance(plotter, BasePlot) else {}
        if rc_params:
            with plt.rc_context(rc=rc_params):
                result = func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        if output:
            if isinstance(result, Figure):
                fig = result
            else:
                fig = plt.gcf()

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, dpi=300, bbox_inches="tight")

        return result

    return cast(F, wrapper)


class BasePlot(ABC):
    """
    zh: 所有绘图类的抽象基类。
    en: Abstract base class for all plotting classes.
    """

    def __init__(self, theme: str = "default"):
        """
        zh: 初始化绘图类。
        en: Initialize the plotting class.

        Args:
            theme (str, optional):
                zh: 主题名称或路径
                en: Theme name or path
        """
        self.theme = theme
        set_theme(theme)

        self.theme_obj = None
        if theme in THEMES:
            self.theme_obj = THEMES[theme]
        else:
            self.theme_obj = load_custom_theme(theme)

    def infer_chart_type(self) -> str:
        class_name = self.__class__.__name__
        if class_name.lower().endswith("plot"):
            return class_name[:-4].lower()
        return class_name.lower()

    def _get_chart_params_raw(self, chart_type: str) -> dict[str, Any]:
        if not self.theme_obj:
            return {}
        params = self.theme_obj.get_chart_params(chart_type)
        if params is None:
            return {}
        if not isinstance(params, dict):
            raise ValueError(f"chart_specific_params['{chart_type}'] must be a dictionary")
        return params

    def get_chart_specific_params(self, chart_type: str) -> dict[str, Any]:
        """
        zh: 获取当前主题中针对该图表类型的特有配置。
        en: Get chart-specific configuration from the current theme.

        Args:
            chart_type (str):
                zh: 图表类型
                en: Chart type

        Returns:
            dict[str, Any]:
                zh: 配置参数字典
                en: Configuration parameters dictionary
        """
        params = self._get_chart_params_raw(chart_type)
        params.pop("rc_params", None)
        return params

    def get_chart_rc_params(self, chart_type: str) -> dict[str, Any]:
        params = self._get_chart_params_raw(chart_type)
        rc_params = params.get("rc_params", {})
        if rc_params is None:
            return {}
        if not isinstance(rc_params, dict):
            raise ValueError(f"chart_specific_params['{chart_type}']['rc_params'] must be a dictionary")
        return rc_params.copy()

    def get_fig_ax(self, figsize: tuple[float, float] | None = None) -> tuple[Figure, Axes]:
        """
        zh: 创建 Figure 和 Axes 对象。
        en: Create Figure and Axes objects.

        Args:
            figsize (tuple[float, float] | None, optional):
                zh: 图表大小
                en: Figure size

        Returns:
            tuple[Figure, Axes]:
                zh: (Figure, Axes) 元组
                en: (Figure, Axes) tuple
        """
        fig, ax = plt.subplots(figsize=figsize)
        return fig, ax

    @abstractmethod
    def plot(self, data: Any, **kwargs: Any) -> Figure:
        """
        zh: 执行绘图逻辑。
        en: Execute plotting logic.

        Args:
            data (Any):
                zh: 数据
                en: Data
            **kwargs:
                zh: 其他参数
                en: Other arguments

        Returns:
            Figure:
                zh: matplotlib Figure 对象
                en: matplotlib Figure object
        """
        pass
