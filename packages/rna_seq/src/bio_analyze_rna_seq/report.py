import pandas as pd
import numpy as np
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from bio_analyze_core.logging import get_logger
from bio_plot.plots.volcano import VolcanoPlot
from bio_plot.plots.heatmap import HeatmapPlot
from bio_plot.plots.pca import PCAPlot

logger = get_logger(__name__)

class ReportGenerator:
    def __init__(
        self,
        output_dir: Path,
        qc_stats: dict,
        counts: pd.DataFrame,
        de_results: pd.DataFrame,
        enrich_results: dict
    ):
        self.output_dir = output_dir
        self.qc_stats = qc_stats
        self.counts = counts
        self.de_results = de_results
        self.enrich_results = enrich_results
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir = self.output_dir / "plots"
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def generate(self):
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
            top_genes_list.append({
                "name": row["sample"] if "sample" in row else row.name, # 索引可能是基因名
                "log2FoldChange": row.get("log2FoldChange", 0),
                "pvalue": row.get("pvalue", 1),
                "padj": row.get("padj", 1)
            })
            
        # 5. 渲染模板
        template_dir = Path(__file__).parent.parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("report.html")
        
        html_content = template.render(
            qc_stats=self.qc_stats,
            pca_plot=f"plots/{pca_plot_path.name}",
            volcano_plot=f"plots/{volcano_plot_path.name}",
            heatmap_plot=f"plots/{heatmap_plot_path.name}",
            top_genes=top_genes_list,
            enrichment_results=self.enrich_results
        )
        
        with open(self.output_dir / "report.html", "w") as f:
            f.write(html_content)
            
        logger.info(f"Report generated at {self.output_dir / 'report.html'}")

    def _generate_pca(self) -> Path:
        # 对数转换
        log_counts = np.log1p(self.counts)
        
        out_path = self.plots_dir / "pca.png"
        
        # 使用 bio_plot 的 PCAPlot
        # counts 是 基因 x 样本 的矩阵
        # PCAPlot 默认 transpose=True，正好适用
        
        plotter = PCAPlot(theme="nature")
        plotter.plot(
            data=log_counts,
            transpose=True, # 基因在行，样本在列 -> 转置
            cluster=True, # 开启聚类（画圈）
            n_clusters=3, # 默认 3，如果有样本分组信息更好，但这里我们没有传入设计矩阵
            # 如果能传入设计矩阵中的分组信息作为 hue 会更好
            # 目前 ReportGenerator 只有 qc_stats, counts, de_results
            # 也许应该在 __init__ 中传入 metadata
            title="PCA of Gene Expression",
            output=str(out_path)
        )
        
        return out_path

    def _generate_volcano(self) -> Path:
        # 使用 bio_plot VolcanoPlot
        # 假设 de_results 有 'log2FoldChange' 和 'padj' 或 'pvalue'
        # 如果需要，重置索引以获取基因名称，但 VolcanoPlot 接受 dataframe
        
        out_path = self.plots_dir / "volcano.png"
        
        # 检查列
        # pydeseq2 结果列：log2FoldChange, pvalue, padj
        
        plotter = VolcanoPlot(theme="nature")
        plotter.plot(
            data=self.de_results.reset_index(), # 重置索引以确保列可用
            x="log2FoldChange",
            y="padj", # 使用调整后的 p-value
            title="Volcano Plot",
            output=str(out_path)
        )
        return out_path

    def _generate_heatmap(self) -> Path:
        # 前 50 个高变基因或前 50 个差异表达基因
        # 这里取前 50 个显著差异表达基因
        sig_genes = self.de_results[self.de_results["padj"] < 0.05].sort_values("padj").head(50).index
        
        if len(sig_genes) < 2:
            # 如果没有差异表达基因，回退到高变基因
            variances = self.counts.var(axis=1)
            sig_genes = variances.sort_values(ascending=False).head(50).index
            
        subset_counts = np.log1p(self.counts.loc[sig_genes])
        
        out_path = self.plots_dir / "heatmap.png"
        
        plotter = HeatmapPlot(theme="nature")
        plotter.plot(
            data=subset_counts,
            cluster_rows=True,
            cluster_cols=True,
            z_score=0, # Z-score 行
            title="Top DE Genes Heatmap",
            output=str(out_path)
        )
        return out_path
