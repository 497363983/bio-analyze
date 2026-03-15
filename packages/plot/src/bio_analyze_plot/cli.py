from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from bio_analyze_core.cli_i18n import detect_language, localize_app

from .plots.bar import BarPlot
from .plots.box import BoxPlot
from .plots.chromosome import ChromosomePlot
from .plots.gsea import GSEAPlot
from .plots.heatmap import HeatmapPlot
from .plots.line import LinePlot
from .plots.pca import PCAPlot
from .plots.pie import PiePlot
from .plots.scatter import ScatterPlot
from .plots.volcano import VolcanoPlot


def read_data(input_path: Path, sheet: str | None = None) -> pd.DataFrame:
    """
    zh: 从 CSV、TSV 或 Excel 文件读取数据。
    en: Read data from CSV, TSV, or Excel file.

    Args:
        input_path (Path):
            zh: 输入文件路径
            en: Input file path
        sheet (str | None, optional):
            zh: Excel 工作表名称
            en: Excel sheet name

    Returns:
        pd.DataFrame:
            zh: 读取的数据
            en: Loaded data
    """
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
    app = typer.Typer(help="zh: 绘图工具\nen: Publication-ready plotting tools.")

    @app.command("volcano")
    def _volcano(
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(
            ...,
            "-o",
            "--output",
            help="zh: 输出文件路径 (例如 volcano.png)。\nen: Output file path (e.g. volcano.png).",
        ),
        x: str = typer.Option(
            "log2FoldChange", help="zh: log2 fold change 列名。\nen: Column name for log2 fold change."
        ),
        y: str = typer.Option("pvalue", help="zh: p-value 列名。\nen: Column name for p-value."),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        fc_cutoff: float = typer.Option(1.0, help="zh: Fold change 截断值。\nen: Fold change cutoff."),
        p_cutoff: float = typer.Option(0.05, help="zh: P-value 截断值。\nen: P-value cutoff."),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    ) -> None:
        """
        zh: 从数据生成火山图。
        en: Generate volcano plot from data.
        """
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
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        x: str = typer.Option(..., help="zh: X 轴列名。\nen: Column name for X-axis."),
        y: str = typer.Option(..., help="zh: Y 轴列名。\nen: Column name for Y-axis."),
        hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
        error_bar_type: str = typer.Option(None, help="zh: 误差棒类型: SD, SE, CI。\nen: Error bar type: SD, SE, CI."),
        error_bar_ci: float = typer.Option(
            95, help="zh: 置信区间大小 (默认: 95)。\nen: Confidence interval size (default: 95)."
        ),
        error_bar_capsize: float = typer.Option(
            3.0, help="zh: 误差棒帽大小 (以点为单位)。\nen: Error bar capsize (in points)."
        ),
        markers: bool = typer.Option(
            False, help="zh: 为数据点使用默认标记。\nen: Use default markers for data points."
        ),
        marker_style: str = typer.Option(
            None,
            help="zh: 指定标记符号 (逗号分隔, 例如 'o,s')。覆盖 --markers。\nen: Specific marker symbols (comma-separated, e.g. 'o,s'). Overrides --markers.",
        ),
        dashes: bool = typer.Option(True, help="zh: 为线条使用虚线样式。\nen: Use dashes for lines."),
        smooth: bool = typer.Option(False, help="zh: 启用平滑曲线拟合。\nen: Enable smooth curve fitting."),
        smooth_points: int = typer.Option(300, help="zh: 插值点数。\nen: Number of points for interpolation."),
    ) -> None:
        """
        zh: 生成折线图。
        en: Generate line plot.
        """
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
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        x: str = typer.Option(..., help="zh: X 轴列名。\nen: Column name for X-axis."),
        y: str = typer.Option(..., help="zh: Y 轴列名。\nen: Column name for Y-axis."),
        hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        error_bar_type: str = typer.Option(None, help="zh: 误差棒类型: SD, SE, CI。\nen: Error bar type: SD, SE, CI."),
        error_bar_ci: float = typer.Option(
            95, help="zh: 置信区间大小 (默认: 95)。\nen: Confidence interval size (default: 95)."
        ),
        error_bar_max: str = typer.Option(
            None, help="zh: 误差棒上限列名。\nen: Column name for error bar upper limit."
        ),
        error_bar_min: str = typer.Option(
            None, help="zh: 误差棒下限列名。\nen: Column name for error bar lower limit."
        ),
        error_bar_capsize: float = typer.Option(0.1, help="zh: 误差棒帽大小。\nen: Error bar capsize."),
        significance: list[str] = typer.Option(
            None, help="zh: 显著性检验配对 (例如 'A,B' 'C,D')。\nen: Pairs for significance testing (e.g. 'A,B' 'C,D')."
        ),
        test: str = typer.Option("t-test_ind", help="zh: 统计检验方法。\nen: Statistical test method."),
        text_format: str = typer.Option("star", help="zh: 显著性标注格式。\nen: Significance annotation format."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    ) -> None:
        """
        zh: 生成柱状图。
        en: Generate bar plot.
        """
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
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        x: str = typer.Option(..., help="zh: X 轴列名。\nen: Column name for X-axis."),
        y: str = typer.Option(..., help="zh: Y 轴列名。\nen: Column name for Y-axis."),
        hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        significance: list[str] = typer.Option(
            None, help="zh: 显著性检验配对 (例如 'A,B' 'C,D')。\nen: Pairs for significance testing (e.g. 'A,B' 'C,D')."
        ),
        test: str = typer.Option("t-test_ind", help="zh: 统计检验方法。\nen: Statistical test method."),
        text_format: str = typer.Option("star", help="zh: 显著性标注格式。\nen: Significance annotation format."),
        add_swarm: bool = typer.Option(False, help="zh: 叠加蜂群图点。\nen: Overlay swarmplot points."),
        swarm_color: str = typer.Option(".25", help="zh: 蜂群图点颜色。\nen: Swarmplot point color."),
        swarm_size: float = typer.Option(3.0, help="zh: 蜂群图点大小。\nen: Swarmplot point size."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    ) -> None:
        """
        zh: 生成箱线图。
        en: Generate box plot.
        """
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
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        index_col: str = typer.Option(None, help="zh: 用作行索引的列。\nen: Column to use as row index."),
        cluster_rows: bool = typer.Option(True, help="zh: 是否聚类行。\nen: Whether to cluster rows."),
        cluster_cols: bool = typer.Option(True, help="zh: 是否聚类列。\nen: Whether to cluster columns."),
        z_score: int = typer.Option(
            None,
            help="zh: 标准化 (0: 行, 1: 列)。None 禁用。\nen: 0 (rows) or 1 (columns) for standardization. None to disable.",
        ),
        cmap: str = typer.Option(
            None, help="zh: 颜色映射名称 (例如 'vlag', 'coolwarm')。\nen: Colormap name (e.g. 'vlag', 'coolwarm')."
        ),
        center: float = typer.Option(None, help="zh: 颜色映射居中的值。\nen: Value at which to center the colormap."),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    ) -> None:
        """
        zh: 生成热图/聚类图。
        en: Generate heatmap/clustermap.
        """
        df = read_data(input_file, sheet=sheet)

        # 准备传递给 plot 的 kwargs，过滤掉 None 的值以允许使用默认值/主题值
        kwargs = {}
        if cmap is not None:
            kwargs["cmap"] = cmap
        if center is not None:
            kwargs["center"] = center

        plotter = HeatmapPlot(theme=theme)
        plotter.plot(
            data=df,
            index_col=index_col,
            cluster_rows=cluster_rows,
            cluster_cols=cluster_cols,
            z_score=z_score,
            title=title,
            output=str(output),
            **kwargs,
        )
        typer.echo(f"Saved heatmap to {output}")

    @app.command("pca")
    def _pca(
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
        style: str = typer.Option(None, help="zh: 标记样式列名。\nen: Column name for marker style."),
        size: str = typer.Option(None, help="zh: 标记大小列名。\nen: Column name for marker size."),
        index_col: str = typer.Option(
            None, help="zh: 用作索引的列 (例如基因名)。\nen: Column to use as index (e.g. gene names)."
        ),
        transpose: bool = typer.Option(
            True,
            help="zh: 转置输入数据 (默认: True, 假设 Genes x Samples)。\nen: Transpose input data (default: True, assumes Genes x Samples).",
        ),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        cluster: bool = typer.Option(False, help="zh: 执行 KMeans 聚类。\nen: Perform KMeans clustering."),
        n_clusters: int = typer.Option(3, help="zh: KMeans 聚类的簇数。\nen: Number of clusters for KMeans."),
        add_ellipse: bool = typer.Option(
            False, help="zh: 为每个分组绘制置信椭圆。\nen: Draw confidence ellipses for each group."
        ),
        ellipse_std: float = typer.Option(
            2.0, help="zh: 置信椭圆的标准差。\nen: Standard deviation for confidence ellipses."
        ),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    ) -> None:
        """
        zh: 生成 PCA 图。
        en: Generate PCA plot.
        """
        df = read_data(input_file, sheet=sheet)
        plotter = PCAPlot(theme=theme)
        plotter.plot(
            data=df,
            hue=hue,
            style=style,
            size=size,
            index_col=index_col,
            transpose=transpose,
            title=title,
            cluster=cluster,
            n_clusters=n_clusters,
            add_ellipse=add_ellipse,
            ellipse_std=ellipse_std,
            output=str(output),
        )
        typer.echo(f"Saved PCA plot to {output}")

    @app.command("scatter")
    def _scatter(
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        x: str = typer.Option(..., help="zh: X 轴列名。\nen: Column name for X-axis."),
        y: str = typer.Option(..., help="zh: Y 轴列名。\nen: Column name for Y-axis."),
        hue: str = typer.Option(None, help="zh: 分组列名 (hue)。\nen: Grouping column name (hue)."),
        style: str = typer.Option(None, help="zh: 标记样式列名。\nen: Column name for marker style."),
        size: str = typer.Option(None, help="zh: 标记大小列名。\nen: Column name for marker size."),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        add_ellipse: bool = typer.Option(
            False, help="zh: 为每个分组绘制置信椭圆。\nen: Draw confidence ellipses for each group."
        ),
        ellipse_std: float = typer.Option(
            2.0, help="zh: 置信椭圆的标准差。\nen: Standard deviation for confidence ellipses."
        ),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    ) -> None:
        """
        zh: 生成散点图。
        en: Generate scatter plot.
        """
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
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        x: str = typer.Option(..., help="zh: 标签列名 (分类变量)。\nen: Column name for labels (categorical)."),
        y: str = typer.Option(..., help="zh: 数值列名。\nen: Column name for values (numerical)."),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        autopct: str = typer.Option("%1.1f%%", help="zh: 百分比格式。\nen: Percentage format."),
        startangle: float = typer.Option(90, help="zh: 起始角度。\nen: Start angle."),
        explode: str = typer.Option(
            None,
            help="zh: 扇区偏移。可以是列名或逗号分隔的数值。\nen: Explode slices. Can be a column name or comma-separated values.",
        ),
        shadow: bool = typer.Option(False, help="zh: 显示阴影。\nen: Show shadow."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
    ) -> None:
        """
        zh: 生成饼图。
        en: Generate pie chart.
        """
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
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        rank: str = typer.Option("rank", help="zh: 排名列名 (X 轴)。\nen: Column name for rank (x-axis)."),
        score: str = typer.Option(
            "running_es", help="zh: 运行富集得分列名 (Y 轴)。\nen: Column name for running ES (y-axis)."
        ),
        hit: str = typer.Option(
            "hit", help="zh: 命中状态列名 (0/1 或布尔值)。\nen: Column name for hit status (0/1 or boolean)."
        ),
        metric: str = typer.Option(
            None, help="zh: 排名指标列名 (Y 轴底部)。\nen: Column name for ranking metric (y-axis bottom)."
        ),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
        color: str = typer.Option("#4DAF4A", help="zh: 富集得分曲线颜色。\nen: Color for enrichment score line."),
        hit_color: str = typer.Option("black", help="zh: 命中线条颜色。\nen: Color for hit lines."),
        nes: float = typer.Option(None, help="zh: 标准化富集得分 (NES)。\nen: Normalized Enrichment Score."),
        pvalue: float = typer.Option(None, help="zh: P-value。\nen: P-value."),
        fdr: float = typer.Option(None, help="zh: FDR q-value。\nen: FDR q-value."),
        show_border: bool = typer.Option(True, help="zh: 显示顶部和右侧边框。\nen: Show top and right borders."),
    ) -> None:
        """
        zh: 生成 GSEA 富集图。
        en: Generate GSEA enrichment plot.
        """
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
        input_file: Path = typer.Argument(
            ..., help="zh: 输入文件路径 (CSV, TSV 或 Excel)。\nen: Input file path (CSV, TSV, or Excel)."
        ),
        output: Path = typer.Option(..., "-o", "--output", help="zh: 输出文件路径。\nen: Output file path."),
        chrom_col: str = typer.Option("chrom", help="zh: 染色体列名。\nen: Column name for chromosome."),
        pos_col: str = typer.Option("pos", help="zh: 位置列名。\nen: Column name for position."),
        pos_counts_col: str = typer.Option(
            "pos_counts", help="zh: 正链计数列名。\nen: Column name for positive strand counts."
        ),
        neg_counts_col: str = typer.Option(
            "neg_counts", help="zh: 负链计数列名。\nen: Column name for negative strand counts."
        ),
        theme: str = typer.Option(
            "nature",
            help="zh: 绘图主题 (nature, science, default) 或自定义主题路径 (.json/.py)。\nen: Plot theme (nature, science, default) or path to custom theme (.json/.py).",
        ),
        title: str = typer.Option(None, help="zh: 图表标题。\nen: Plot title."),
        sheet: str = typer.Option(None, help="zh: Excel 工作表名称。\nen: Sheet name for Excel files."),
        max_chroms: int = typer.Option(
            24, help="zh: 显示的最大染色体数量。\nen: Maximum number of chromosomes to display."
        ),
    ) -> None:
        """
        zh: 生成染色体覆盖度分布图。
        en: Generate chromosome coverage distribution plot.
        """
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

    localize_app(app, detect_language())
    return app
