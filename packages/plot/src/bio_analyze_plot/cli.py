from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from .plots.bar import BarPlot
from .plots.box import BoxPlot
from .plots.gsea import GSEAPlot
from .plots.heatmap import HeatmapPlot
from .plots.line import LinePlot
from .plots.pca import PCAPlot
from .plots.pie import PiePlot
from .plots.scatter import ScatterPlot
from .plots.volcano import VolcanoPlot
from .plots.chromosome import ChromosomePlot

def read_data(input_path: Path, sheet: str | None = None) -> pd.DataFrame:
    """从 CSV、TSV 或 Excel 文件读取数据。"""
    suffix = input_path.suffix.lower()
    if suffix in [".csv"]:
        return pd.read_csv(input_path)
    elif suffix in [".tsv", ".txt"]:
        return pd.read_csv(input_path, sep="\t")
    elif suffix in [".xlsx", ".xls"]:
        if sheet:
            return pd.read_excel(input_path, sheet_name=sheet)
        return pd.read_excel(input_path)
    else:
        # 默认为 csv
        return pd.read_csv(input_path)


def get_app() -> typer.Typer:
    app = typer.Typer(help="Publication-ready plotting tools.")

    @app.command("volcano")
    def _volcano(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path (e.g. volcano.png)."),
        x: str = typer.Option("log2FoldChange", help="Column name for log2 fold change."),
        y: str = typer.Option("pvalue", help="Column name for p-value."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        fc_cutoff: float = typer.Option(1.0, help="Fold change cutoff."),
        p_cutoff: float = typer.Option(0.05, help="P-value cutoff."),
        title: str = typer.Option(None, help="Plot title."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
    ) -> None:
        """从数据生成火山图。"""
        df = read_data(input_file, sheet=sheet)
        plotter = VolcanoPlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            fc_cutoff=fc_cutoff,
            p_cutoff=p_cutoff,
            title=title,
            output=str(output),
        )
        typer.echo(f"Saved volcano plot to {output}")

    @app.command("line")
    def _line(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        x: str = typer.Option(..., help="Column name for X-axis."),
        y: str = typer.Option(..., help="Column name for Y-axis."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
        error_bar_type: str = typer.Option(None, help="Error bar type: SD, SE, CI."),
        error_bar_ci: float = typer.Option(95, help="Confidence interval size (default: 95)."),
        error_bar_capsize: float = typer.Option(3.0, help="Error bar capsize (in points)."),
        markers: bool = typer.Option(False, help="Use default markers for data points."),
        marker_style: str = typer.Option(None, help="Specific marker symbols (comma-separated, e.g. 'o,s'). Overrides --markers."),
        dashes: bool = typer.Option(True, help="Use dashes for lines."),
        smooth: bool = typer.Option(False, help="Enable smooth curve fitting."),
        smooth_points: int = typer.Option(300, help="Number of points for interpolation."),
    ) -> None:
        """生成折线图。"""
        df = read_data(input_file, sheet=sheet)
        
        # Parse markers
        markers_arg = markers
        if marker_style:
            if "," in marker_style:
                markers_arg = [m.strip() for m in marker_style.split(",")]
            else:
                markers_arg = marker_style

        plotter = LinePlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            title=title,
            output=str(output),
            error_bar_type=error_bar_type,
            error_bar_ci=error_bar_ci,
            error_bar_capsize=error_bar_capsize,
            markers=markers_arg,
            dashes=dashes,
            smooth=smooth,
            smooth_points=smooth_points,
        )
        typer.echo(f"Saved line plot to {output}")

    @app.command("bar")
    def _bar(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        x: str = typer.Option(..., help="Column name for X-axis."),
        y: str = typer.Option(..., help="Column name for Y-axis."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        error_bar_type: str = typer.Option(None, help="Error bar type: SD, SE, CI."),
        error_bar_ci: float = typer.Option(95, help="Confidence interval size (default: 95)."),
        error_bar_max: str = typer.Option(None, help="Column name for error bar upper limit."),
        error_bar_min: str = typer.Option(None, help="Column name for error bar lower limit."),
        error_bar_capsize: float = typer.Option(0.1, help="Error bar capsize."),
        significance: list[str] = typer.Option(None, help="Pairs for significance testing (e.g. 'A,B' 'C,D')."),
        test: str = typer.Option("t-test_ind", help="Statistical test method."),
        text_format: str = typer.Option("star", help="Significance annotation format."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
    ) -> None:
        """生成柱状图。"""
        df = read_data(input_file, sheet=sheet)

        # 解析显著性对
        sig_pairs = []
        if significance:
            for pair_str in significance:
                parts = pair_str.split(",")
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
            text_format=text_format,
        )
        typer.echo(f"Saved bar plot to {output}")

    @app.command("box")
    def _box(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        x: str = typer.Option(..., help="Column name for X-axis."),
        y: str = typer.Option(..., help="Column name for Y-axis."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        significance: list[str] = typer.Option(None, help="Pairs for significance testing (e.g. 'A,B' 'C,D')."),
        test: str = typer.Option("t-test_ind", help="Statistical test method."),
        text_format: str = typer.Option("star", help="Significance annotation format."),
        add_swarm: bool = typer.Option(False, help="Overlay swarmplot points."),
        swarm_color: str = typer.Option(".25", help="Swarmplot point color."),
        swarm_size: float = typer.Option(3.0, help="Swarmplot point size."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
    ) -> None:
        """生成箱线图。"""
        df = read_data(input_file, sheet=sheet)

        # 解析显著性对
        sig_pairs = []
        if significance:
            for pair_str in significance:
                parts = pair_str.split(",")
                if len(parts) == 2:
                    sig_pairs.append((parts[0].strip(), parts[1].strip()))

        plotter = BoxPlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            title=title,
            output=str(output),
            significance=sig_pairs if sig_pairs else None,
            test=test,
            text_format=text_format,
            add_swarm=add_swarm,
            swarm_color=swarm_color,
            swarm_size=swarm_size,
        )
        typer.echo(f"Saved box plot to {output}")

    @app.command("heatmap")
    def _heatmap(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        index_col: str = typer.Option(None, help="Column to use as row index."),
        cluster_rows: bool = typer.Option(True, help="Whether to cluster rows."),
        cluster_cols: bool = typer.Option(True, help="Whether to cluster columns."),
        z_score: int = typer.Option(None, help="0 (rows) or 1 (columns) for standardization. None to disable."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
    ) -> None:
        """生成热图/聚类图。"""
        df = read_data(input_file, sheet=sheet)
        plotter = HeatmapPlot(theme=theme)
        plotter.plot(
            data=df,
            index_col=index_col,
            cluster_rows=cluster_rows,
            cluster_cols=cluster_cols,
            z_score=z_score,
            title=title,
            output=str(output),
        )
        typer.echo(f"Saved heatmap to {output}")

    @app.command("pca")
    def _pca(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        index_col: str = typer.Option(None, help="Column to use as index (e.g. gene names)."),
        transpose: bool = typer.Option(True, help="Transpose input data (default: True, assumes Genes x Samples)."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        cluster: bool = typer.Option(False, help="Perform KMeans clustering."),
        n_clusters: int = typer.Option(3, help="Number of clusters for KMeans."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
    ) -> None:
        """生成 PCA 图。"""
        df = read_data(input_file, sheet=sheet)
        plotter = PCAPlot(theme=theme)
        plotter.plot(
            data=df,
            hue=hue,
            index_col=index_col,
            transpose=transpose,
            title=title,
            cluster=cluster,
            n_clusters=n_clusters,
            output=str(output),
        )
        typer.echo(f"Saved PCA plot to {output}")

    @app.command("scatter")
    def _scatter(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        x: str = typer.Option(..., help="Column name for X-axis."),
        y: str = typer.Option(..., help="Column name for Y-axis."),
        hue: str = typer.Option(None, help="Grouping column name (hue)."),
        style: str = typer.Option(None, help="Column name for marker style."),
        size: str = typer.Option(None, help="Column name for marker size."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        add_ellipse: bool = typer.Option(False, help="Draw confidence ellipses for each group."),
        ellipse_std: float = typer.Option(2.0, help="Standard deviation for confidence ellipses."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
    ) -> None:
        """生成散点图。"""
        df = read_data(input_file, sheet=sheet)
        plotter = ScatterPlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            hue=hue,
            style=style,
            size=size,
            title=title,
            output=str(output),
            add_ellipse=add_ellipse,
            ellipse_std=ellipse_std,
        )
        typer.echo(f"Saved scatter plot to {output}")

    @app.command("pie")
    def _pie(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        x: str = typer.Option(..., help="Column name for labels (categorical)."),
        y: str = typer.Option(..., help="Column name for values (numerical)."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        autopct: str = typer.Option("%1.1f%%", help="Percentage format."),
        startangle: float = typer.Option(90, help="Start angle."),
        explode: str = typer.Option(None, help="Explode slices. Can be a column name or comma-separated values."),
        shadow: bool = typer.Option(False, help="Show shadow."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
    ) -> None:
        """生成饼图。"""
        df = read_data(input_file, sheet=sheet)

        explode_arg = None
        if explode:
            if explode in df.columns:
                explode_arg = explode
            else:
                try:
                    explode_arg = [float(v.strip()) for v in explode.split(",")]
                except ValueError:
                    explode_arg = None
                    typer.echo(f"Warning: Invalid explode format '{explode}'. Ignored.")

        plotter = PiePlot(theme=theme)
        plotter.plot(
            data=df,
            x=x,
            y=y,
            title=title,
            autopct=autopct,
            startangle=startangle,
            explode=explode_arg,
            shadow=shadow,
            output=str(output),
        )
        typer.echo(f"Saved pie chart to {output}")

    @app.command("gsea")
    def _gsea(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        rank: str = typer.Option("rank", help="Column name for rank (x-axis)."),
        score: str = typer.Option("running_es", help="Column name for running ES (y-axis)."),
        hit: str = typer.Option("hit", help="Column name for hit status (0/1 or boolean)."),
        metric: str = typer.Option(None, help="Column name for ranking metric (y-axis bottom)."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
        color: str = typer.Option("#4DAF4A", help="Color for enrichment score line."),
        hit_color: str = typer.Option("black", help="Color for hit lines."),
        nes: float = typer.Option(None, help="Normalized Enrichment Score."),
        pvalue: float = typer.Option(None, help="P-value."),
        fdr: float = typer.Option(None, help="FDR q-value."),
        show_border: bool = typer.Option(True, help="Show top and right borders."),
    ) -> None:
        """生成 GSEA 富集图。"""
        df = read_data(input_file, sheet=sheet)
        plotter = GSEAPlot(theme=theme)
        plotter.plot(
            data=df,
            rank=rank,
            score=score,
            hit=hit,
            metric=metric,
            title=title,
            output=str(output),
            color=color,
            hit_color=hit_color,
            nes=nes,
            pvalue=pvalue,
            fdr=fdr,
            show_border=show_border,
        )
        typer.echo(f"Saved GSEA plot to {output}")

    @app.command("chromosome")
    def _chromosome(
        input_file: Path = typer.Argument(..., help="Input file path (CSV, TSV, or Excel)."),
        output: Path = typer.Option(..., "-o", "--output", help="Output file path."),
        chrom_col: str = typer.Option("chrom", help="Column name for chromosome."),
        pos_col: str = typer.Option("pos", help="Column name for position."),
        pos_counts_col: str = typer.Option("pos_counts", help="Column name for positive strand counts."),
        neg_counts_col: str = typer.Option("neg_counts", help="Column name for negative strand counts."),
        theme: str = typer.Option(
            "nature",
            help="Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="Plot title."),
        sheet: str = typer.Option(None, help="Sheet name for Excel files."),
        max_chroms: int = typer.Option(24, help="Maximum number of chromosomes to display."),
    ) -> None:
        """生成染色体覆盖度分布图。"""
        df = read_data(input_file, sheet=sheet)
        plotter = ChromosomePlot(theme=theme)
        plotter.plot(
            data=df,
            chrom_col=chrom_col,
            pos_col=pos_col,
            pos_counts_col=pos_counts_col,
            neg_counts_col=neg_counts_col,
            max_chroms=max_chroms,
            title=title,
            output=str(output),
        )
        typer.echo(f"Saved chromosome plot to {output}")

    return app
