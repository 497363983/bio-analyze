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
        # 检查 kwargs 中是否有 'output'
        output = kwargs.pop("output", None)

        # 运行绘图函数
        result = func(*args, **kwargs)

        # 如果指定了 output，则保存
        if output:
            if isinstance(result, Figure):
                fig = result
            else:
                # 尝试获取当前 figure
                fig = plt.gcf()

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # 保存
            fig.savefig(output_path, dpi=300, bbox_inches="tight")
            # 不要在保存后关闭，因为可能还要在测试中检查它
            # 或者，如果这是最后一步，应该关闭以释放内存。
            # 但为了测试方便，通常保留对象。
            # 不过 CLI 运行完就退出了。

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

        # 获取当前主题对象，以便访问 chart_specific_params
        # set_theme 已经应用了主题，但我们需要对象本身来获取额外参数
        self.theme_obj = None
        if theme in THEMES:
            self.theme_obj = THEMES[theme]
        else:
            self.theme_obj = load_custom_theme(theme)

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
        if self.theme_obj:
            return self.theme_obj.get_chart_params(chart_type)
        return {}

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
