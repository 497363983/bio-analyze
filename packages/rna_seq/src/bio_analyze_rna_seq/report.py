import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from bio_analyze_plot.plots.heatmap import HeatmapPlot
from bio_analyze_plot.plots.pca import PCAPlot
from bio_analyze_plot.plots.volcano import VolcanoPlot
from jinja2 import Environment, FileSystemLoader

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    zh: 报告生成器。
    en: Report generator.
    """

    def __init__(
        self,
        output_dir: Path,
        qc_stats: dict,
        counts: pd.DataFrame,
        de_results: pd.DataFrame,
        enrich_results: dict,
        gsea_plots: dict[str, Path] | None = None,
        theme: str = "default",
    ):
        """
        zh: 初始化报告生成器。
        en: Initialize the report generator.

        Args:
            output_dir (Path):
                zh: 输出目录路径。
                en: Path to the output directory.
            qc_stats (dict):
                zh: QC 统计信息字典。
                en: Dictionary of QC statistics.
            counts (pd.DataFrame):
                zh: 计数矩阵。
                en: Counts matrix.
            de_results (pd.DataFrame):
                zh: 差异表达分析结果。
                en: Differential expression analysis results.
            enrich_results (dict):
                zh: 富集分析结果。
                en: Enrichment analysis results.
            gsea_plots (dict[str, Path] | None, optional):
                zh: GSEA 绘图路径字典。
                en: Dictionary of GSEA plot paths.
            theme (str, optional):
                zh: 绘图主题。
                en: Plotting theme.
        """
        self.output_dir = output_dir
        self.qc_stats = qc_stats
        self.counts = counts
        self.de_results = de_results
        self.enrich_results = enrich_results
        self.gsea_plots = gsea_plots or {}
        self.theme = theme
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir = self.output_dir / "plots"
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def generate(self):
        """
        zh: 生成 HTML 报告。
        en: Generate HTML report.

        zh: 包括 PCA、火山图、热图、差异表达基因表和富集分析结果。
        en: Includes PCA, volcano plot, heatmap, differential expression gene table, and enrichment analysis results.
        """
        logger.info("Generating report...")

        # 1. 生成 PCA 图
        pca_plot_path = self._generate_pca()

        # 2. 生成火山图
        volcano_plot_path = self._generate_volcano()

        # 3. 生成热图
        heatmap_plot_path = self._generate_heatmap()

        # 4. 为模板准备数据
        top_genes = self.de_results.sort_values("padj").head(20).reset_index()
        top_genes_list = []
        for _, row in top_genes.iterrows():
            top_genes_list.append(
                {
                    "name": row.get("sample", row.name),  # 索引可能是基因名
                    "log2FoldChange": row.get("log2FoldChange", 0),
                    "pvalue": row.get("pvalue", 1),
                    "padj": row.get("padj", 1),
                }
            )

        # 5. 处理 GSEA 图片
        gsea_plot_paths = self._process_gsea_plots()

        # 6. 渲染模板
        template_dir = Path(__file__).parent.parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("report.html")

        html_content = template.render(
            qc_stats=self.qc_stats,
            pca_plot=f"plots/{pca_plot_path.name}",
            volcano_plot=f"plots/{volcano_plot_path.name}",
            heatmap_plot=f"plots/{heatmap_plot_path.name}",
            top_genes=top_genes_list,
            enrichment_results=self.enrich_results,
            gsea_plots=gsea_plot_paths,
        )

        with open(self.output_dir / "report.html", "w") as f:
            f.write(html_content)

        logger.info(f"Report generated at {self.output_dir / 'report.html'}")

    def _generate_pca(self) -> Path:
        """
        zh: 生成 PCA 图。
        en: Generate PCA plot.

        Returns:
            Path:
                zh: PCA 图文件路径。
                en: Path to PCA plot file.
        """
        # 对数转换
        log_counts = np.log1p(self.counts)

        out_path = self.plots_dir / "pca.png"

        # 使用 bio_plot 的 PCAPlot
        # counts 是 基因 x 样本 的矩阵
        # PCAPlot 默认 transpose=True，正好适用

        plotter = PCAPlot(theme=self.theme)
        plotter.plot(
            data=log_counts,
            transpose=True,  # 基因在行，样本在列 -> 转置
            cluster=True,  # 开启聚类（画圈）
            n_clusters=3,  # 默认 3，如果有样本分组信息更好，但这里我们没有传入设计矩阵
            # 如果能传入设计矩阵中的分组信息作为 hue 会更好
            # 目前 ReportGenerator 只有 qc_stats, counts, de_results
            # 也许应该在 __init__ 中传入 metadata
            title="PCA of Gene Expression",
            output=str(out_path),
        )

        return out_path

    def _generate_volcano(self) -> Path:
        """
        zh: 生成火山图。
        en: Generate volcano plot.

        Returns:
            Path:
                zh: 火山图文件路径。
                en: Path to volcano plot file.
        """
        # 使用 bio_plot VolcanoPlot
        # 假设 de_results 有 'log2FoldChange' 和 'padj' 或 'pvalue'
        # 如果需要，重置索引以获取基因名称，但 VolcanoPlot 接受 dataframe

        out_path = self.plots_dir / "volcano.png"

        # 检查列
        # pydeseq2 结果列：log2FoldChange, pvalue, padj

        plotter = VolcanoPlot(theme=self.theme)
        plotter.plot(
            data=self.de_results.reset_index(),  # 重置索引以确保列可用
            x="log2FoldChange",
            y="padj",  # 使用调整后的 p-value
            title="Volcano Plot",
            output=str(out_path),
        )
        return out_path

    def _generate_heatmap(self) -> Path:
        """
        zh: 生成热图。
        en: Generate heatmap.

        Returns:
            Path:
                zh: 热图文件路径。
                en: Path to heatmap file.
        """
        # 前 50 个高变基因或前 50 个差异表达基因
        # 这里取前 50 个显著差异表达基因
        sig_genes = self.de_results[self.de_results["padj"] < 0.05].sort_values("padj").head(50).index

        if len(sig_genes) < 2:
            # 如果没有差异表达基因，回退到高变基因
            variances = self.counts.var(axis=1)
            sig_genes = variances.sort_values(ascending=False).head(50).index

        subset_counts = np.log1p(self.counts.loc[sig_genes])

        out_path = self.plots_dir / "heatmap.png"

        plotter = HeatmapPlot(theme=self.theme)
        plotter.plot(
            data=subset_counts,
            cluster_rows=True,
            cluster_cols=True,
            z_score=0,  # Z-score 行
            title="Top DE Genes Heatmap",
            output=str(out_path),
        )
        return out_path

    def _process_gsea_plots(self) -> dict[str, str]:
        """
        zh: 处理 GSEA 图并返回相对路径。
        en: Process GSEA plots and return relative paths.

        Returns:
            dict[str, str]:
                zh: 术语到相对路径的映射。
                en: Mapping of terms to relative paths.
        """
        processed_plots = {}
        if not self.gsea_plots:
            return processed_plots

        for term, path in self.gsea_plots.items():
            if not path.exists():
                logger.warning(f"GSEA plot not found at {path}")
                continue

            # Copy to plots directory
            dest_name = f"gsea_{path.name}"
            dest_path = self.plots_dir / dest_name
            shutil.copy2(path, dest_path)

            processed_plots[term] = f"plots/{dest_name}"

        return processed_plots
