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
    Decorator to save plot to file.

    Args:
        func (F):
            Plotting function

    Returns:
        F:
            Decorated function
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
            fig = result if isinstance(result, Figure) else plt.gcf()

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, dpi=300, bbox_inches="tight")

        return result

    return cast(F, wrapper)

class BasePlot(ABC):
    """
    Abstract base class for all plotting classes.
    """

    def __init__(self, theme: str = "default"):
        """
        Initialize the plotting class.

        Args:
            theme (str, optional):
                Theme name or path
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
        Get chart-specific configuration from the current theme.

        Args:
            chart_type (str):
                Chart type

        Returns:
            dict[str, Any]:
                Configuration parameters dictionary
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
        Create Figure and Axes objects.

        Args:
            figsize (tuple[float, float] | None, optional):
                Figure size

        Returns:
            tuple[Figure, Axes]:
                (Figure, Axes) tuple
        """
        fig, ax = plt.subplots(figsize=figsize)
        return fig, ax

    @abstractmethod
    def plot(self, data: Any, **kwargs: Any) -> Figure:
        """
        Execute plotting logic.

        Args:
            data (Any):
                Data
            **kwargs:
                Other arguments

        Returns:
            Figure:
                matplotlib Figure object
        """
        pass
