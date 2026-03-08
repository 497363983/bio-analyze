from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .theme import set_theme

F = TypeVar("F", bound=Callable[..., Any])


def save_plot(
    output: Path | str | None = None,
    dpi: int = 300,
    bbox_inches: str = "tight",
    **kwargs: Any
) -> Callable[[F], F]:
    """Decorator to save plot to file."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **func_kwargs: Any) -> Any:
            # Check if 'output' is in kwargs, if so use it
            out_path = func_kwargs.pop("output", output)
            
            # Run the plotting function
            result = func(*args, **func_kwargs)
            
            # If output is specified, save it
            if out_path:
                # If the function returns a Figure, use it. Otherwise use plt.gcf()
                if isinstance(result, Figure):
                    fig = result
                else:
                    fig = plt.gcf()
                
                Path(out_path).parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(out_path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
                plt.close(fig) # Close to free memory
                
            return result
        return cast(F, wrapper)
    return decorator


class BasePlotter:
    """Base class for all plotters."""
    
    def __init__(self, theme: str = "default"):
        self.theme = theme
        set_theme(theme)

    def get_fig_ax(self, figsize: tuple[float, float] | None = None) -> tuple[Figure, Axes]:
        fig, ax = plt.subplots(figsize=figsize)
        return fig, ax
