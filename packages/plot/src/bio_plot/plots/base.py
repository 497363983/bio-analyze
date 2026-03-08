from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..theme import set_theme

F = TypeVar("F", bound=Callable[..., Any])


def save_plot(func: F) -> F:
    """保存图表到文件的装饰器。"""
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
    """所有绘图类的抽象基类。"""
    
    def __init__(self, theme: str = "default"):
        self.theme = theme
        set_theme(theme)

    def get_fig_ax(self, figsize: tuple[float, float] | None = None) -> tuple[Figure, Axes]:
        fig, ax = plt.subplots(figsize=figsize)
        return fig, ax

    @abstractmethod
    def plot(self, data: Any, **kwargs: Any) -> Figure:
        """执行绘图逻辑。"""
        pass
