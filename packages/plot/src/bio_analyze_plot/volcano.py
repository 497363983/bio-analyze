from __future__ import annotations

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .core import BasePlotter, save_plot


class VolcanoPlotter(BasePlotter):
    @save_plot()
    def plot(
        self,
        data: pd.DataFrame,
        x: str = "log2FoldChange",
        y: str = "pvalue",
        log_y: bool = True,
        fc_cutoff: float = 1.0,
        p_cutoff: float = 0.05,
        title: str = "Volcano Plot",
        output: str | None = None,
    ) -> Figure:
        """
        Draw a volcano plot.

        Args:
            data: DataFrame containing the data.
            x: Column name for log2 fold change.
            y: Column name for p-value (or adj. p-value).
            log_y: Whether to -log10 transform the y-axis.
            fc_cutoff: Fold change cutoff (absolute value).
            p_cutoff: P-value cutoff.
            title: Title of the plot.
            output: Path to save the plot.
        """
        df = data.copy()

        # Calculate -log10(pvalue) if needed
        if log_y:
            y_col = f"-log10({y})"
            df[y_col] = -np.log10(df[y])
        else:
            y_col = y

        # Define groups
        conditions = [
            (df[x] >= fc_cutoff) & (df[y] <= p_cutoff),
            (df[x] <= -fc_cutoff) & (df[y] <= p_cutoff),
        ]
        choices = ["Up", "Down"]
        df["group"] = np.select(conditions, choices, default="Not Sig")

        # Color palette
        palette = {"Up": "#E41A1C", "Down": "#377EB8", "Not Sig": "grey"}

        fig, ax = self.get_fig_ax()

        sns.scatterplot(
            data=df,
            x=x,
            y=y_col,
            hue="group",
            palette=palette,
            alpha=0.7,
            edgecolor=None,
            s=15,  # marker size
            ax=ax,
        )

        # Add cutoff lines
        ax.axvline(x=fc_cutoff, color="grey", linestyle="--", linewidth=0.5)
        ax.axvline(x=-fc_cutoff, color="grey", linestyle="--", linewidth=0.5)
        if log_y:
            ax.axhline(y=-np.log10(p_cutoff), color="grey", linestyle="--", linewidth=0.5)
        else:
            ax.axhline(y=p_cutoff, color="grey", linestyle="--", linewidth=0.5)

        ax.set_title(title)

        # Move legend outside or customize
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

        return fig
