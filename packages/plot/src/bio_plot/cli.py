from __future__ import annotations

from pathlib import Path

import typer
import pandas as pd

from .plots.volcano import VolcanoPlot
from .plots.line import LinePlot
from .plots.bar import BarPlot
from .plots.heatmap import HeatmapPlot
from .plots.pca import PCAPlot

def read_data(input_path: Path) -> pd.DataFrame:
    """Read data from CSV, TSV, or Excel file."""
    suffix = input_path.suffix.lower()
    if suffix in [".csv"]:
        return pd.read_csv(input_path)
    elif suffix in [".tsv", ".txt"]:
        return pd.read_csv(input_path, sep="\t")
    elif suffix in [".xlsx", ".xls"]:
        return pd.read_excel(input_path)
    else:
        # Default to csv
        return pd.read_csv(input_path)

def get_app() -> typer.Typer:
    app = typer.Typer(help="Publication-ready plotting tools.")

    @app.command("volcano")
    def _volcano(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path (e.g. volcano.png)."),
        x: str = typer.Option("log2FoldChange", help="Column name for log2 fold change."),
        y: str = typer.Option("pvalue", help="Column name for p-value."),
        theme: str = typer.Option("nature", help="Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
        fc_cutoff: float = typer.Option(1.0, help="Fold change cutoff."),
        p_cutoff: float = typer.Option(0.05, help="P-value cutoff."),
        title: str = typer.Option("Volcano Plot", help="Plot title.")
    ) -> None:
        """Generate a volcano plot from data."""
        df = read_data(input_file)
        plotter = VolcanoPlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            fc_cutoff=fc_cutoff,
            p_cutoff=p_cutoff,
            title=title,
            output=str(output)
        )
        typer.echo(f"Saved volcano plot to {output}")

    @app.command("line")
    def _line(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        x: str = typer.Option(..., help="Column name for X-axis."),
        y: str = typer.Option(..., help="Column name for Y-axis."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        theme: str = typer.Option("nature", help="Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
        title: str = typer.Option("Line Plot", help="Plot title.")
    ) -> None:
        """Generate a line plot."""
        df = read_data(input_file)
        plotter = LinePlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            title=title,
            output=str(output)
        )
        typer.echo(f"Saved line plot to {output}")

    @app.command("bar")
    def _bar(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        x: str = typer.Option(..., help="Column name for X-axis."),
        y: str = typer.Option(..., help="Column name for Y-axis."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        theme: str = typer.Option("nature", help="Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
        title: str = typer.Option("Bar Plot", help="Plot title."),
        error_bar_type: str = typer.Option(None, help="Error bar type: SD, SE, CI."),
        error_bar_ci: float = typer.Option(95, help="Confidence interval size (default: 95)."),
        error_bar_max: str = typer.Option(None, help="Column name for error bar upper limit."),
        error_bar_min: str = typer.Option(None, help="Column name for error bar lower limit."),
        error_bar_capsize: float = typer.Option(0.1, help="Error bar capsize."),
        significance: list[str] = typer.Option(None, help="Pairs for significance testing (e.g. 'A,B' 'C,D')."),
        test: str = typer.Option("t-test_ind", help="Statistical test method."),
        text_format: str = typer.Option("star", help="Significance annotation format.")
    ) -> None:
        """Generate a bar plot."""
        df = read_data(input_file)
        
        # Parse significance pairs
        sig_pairs = []
        if significance:
            for pair_str in significance:
                parts = pair_str.split(',')
                if len(parts) == 2:
                    sig_pairs.append((parts[0].strip(), parts[1].strip()))
        
        plotter = BarPlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            title=title,
            output=str(output),
            error_bar_type=error_bar_type,
            error_bar_ci=error_bar_ci,
            error_bar_max=error_bar_max,
            error_bar_min=error_bar_min,
            error_bar_capsize=error_bar_capsize,
            significance=sig_pairs if sig_pairs else None,
            test=test,
            text_format=text_format
        )
        typer.echo(f"Saved bar plot to {output}")

    @app.command("heatmap")
    def _heatmap(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        index_col: str = typer.Option(None, help="Column to use as row index."),
        cluster_rows: bool = typer.Option(True, help="Whether to cluster rows."),
        cluster_cols: bool = typer.Option(True, help="Whether to cluster columns."),
        z_score: int = typer.Option(None, help="0 (rows) or 1 (columns) for standardization. None to disable."),
        theme: str = typer.Option("nature", help="Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
        title: str = typer.Option("Heatmap", help="Plot title.")
    ) -> None:
        """Generate a heatmap/clustermap."""
        df = read_data(input_file)
        plotter = HeatmapPlot(theme=theme)
        plotter.plot(
            data=df,
            index_col=index_col,
            cluster_rows=cluster_rows,
            cluster_cols=cluster_cols,
            z_score=z_score,
            title=title,
            output=str(output)
        )
        typer.echo(f"Saved heatmap to {output}")

    @app.command("pca")
    def _pca(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        index_col: str = typer.Option(None, help="Column to use as index (e.g. gene names)."),
        transpose: bool = typer.Option(True, help="Transpose input data (default: True, assumes Genes x Samples)."),
        theme: str = typer.Option("nature", help="Plot theme (nature, science, default) or path to custom theme (.json/.py)."),
        title: str = typer.Option("PCA Plot", help="Plot title."),
        cluster: bool = typer.Option(False, help="Perform KMeans clustering."),
        n_clusters: int = typer.Option(3, help="Number of clusters for KMeans.")
    ) -> None:
        """Generate a PCA plot."""
        df = read_data(input_file)
        plotter = PCAPlot(theme=theme)
        plotter.plot(
            data=df,
            hue=hue,
            index_col=index_col,
            transpose=transpose,
            title=title,
            cluster=cluster,
            n_clusters=n_clusters,
            output=str(output)
        )
        typer.echo(f"Saved PCA plot to {output}")

    return app
