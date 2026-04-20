"""RNA-Seq report generation helpers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from bio_analyze_plot.plots.heatmap import HeatmapPlot
from bio_analyze_plot.plots.pca import PCAPlot
from bio_analyze_plot.plots.volcano import VolcanoPlot
from jinja2 import Environment, FileSystemLoader, Template

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)

_FALLBACK_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>RNA-Seq Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    img { max-width: 100%; height: auto; margin-bottom: 1rem; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }
    th { background: #f5f5f5; }
    section { margin-bottom: 2rem; }
  </style>
</head>
<body>
  <h1>RNA-Seq Analysis Report</h1>
  <section>
    <h2>QC Statistics</h2>
    <pre>{{ qc_stats }}</pre>
  </section>
  <section>
    <h2>PCA</h2>
    <img src="{{ pca_plot }}" alt="PCA plot">
  </section>
  <section>
    <h2>Volcano Plot</h2>
    <img src="{{ volcano_plot }}" alt="Volcano plot">
  </section>
  <section>
    <h2>Heatmap</h2>
    <img src="{{ heatmap_plot }}" alt="Heatmap">
  </section>
  <section>
    <h2>Top Differentially Expressed Genes</h2>
    <table>
      <thead>
        <tr>
          <th>Gene</th>
          <th>log2FoldChange</th>
          <th>pvalue</th>
          <th>padj</th>
        </tr>
      </thead>
      <tbody>
      {% for gene in top_genes %}
        <tr>
          <td>{{ gene.name }}</td>
          <td>{{ gene.log2FoldChange }}</td>
          <td>{{ gene.pvalue }}</td>
          <td>{{ gene.padj }}</td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  </section>
  <section>
    <h2>Enrichment Results</h2>
    <pre>{{ enrichment_results }}</pre>
  </section>
  <section>
    <h2>GSEA Plots</h2>
    {% for term, path in gsea_plots.items() %}
      <div>
        <h3>{{ term }}</h3>
        <img src="{{ path }}" alt="{{ term }}">
      </div>
    {% endfor %}
  </section>
</body>
</html>
"""


class ReportGenerator:
    """Generate a simple HTML report for the RNA-Seq pipeline."""

    def __init__(
        self,
        output_dir: Path,
        qc_stats: dict[str, Any],
        counts: pd.DataFrame,
        de_results: pd.DataFrame,
        enrich_results: dict[str, Any],
        gsea_plots: dict[str, Path] | None = None,
        theme: str = "default",
    ) -> None:
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

    def generate(self) -> Path:
        """Render plots and write the final report HTML file."""
        logger.info("Generating report...")

        pca_plot_path = self._generate_pca()
        volcano_plot_path = self._generate_volcano()
        heatmap_plot_path = self._generate_heatmap()
        gsea_plot_paths = self._process_gsea_plots()
        top_genes = self._prepare_top_genes()

        template = self._load_template()
        html_content = template.render(
            qc_stats=self.qc_stats,
            pca_plot=f"plots/{pca_plot_path.name}",
            volcano_plot=f"plots/{volcano_plot_path.name}",
            heatmap_plot=f"plots/{heatmap_plot_path.name}",
            top_genes=top_genes,
            enrichment_results=self.enrich_results,
            gsea_plots=gsea_plot_paths,
        )

        report_path = self.output_dir / "report.html"
        report_path.write_text(html_content, encoding="utf-8")
        logger.info("Report generated at %s", report_path)
        return report_path

    def _load_template(self) -> Template:
        """Load a packaged report template or fall back to an inline template."""
        template_dir = Path(__file__).resolve().parents[2] / "templates"
        template_path = template_dir / "report.html"
        if template_path.exists():
            env = Environment(loader=FileSystemLoader(str(template_dir)))
            return env.get_template("report.html")
        return Template(_FALLBACK_REPORT_TEMPLATE)

    def _prepare_top_genes(self) -> list[dict[str, Any]]:
        """Build a compact table of top-ranked DE genes for the report."""
        if self.de_results.empty:
            return []

        sort_column = "padj" if "padj" in self.de_results.columns else "pvalue"
        if sort_column in self.de_results.columns:
            top_genes = self.de_results.sort_values(sort_column).head(20)
        else:
            top_genes = self.de_results.head(20)

        rows: list[dict[str, Any]] = []
        for gene_name, row in top_genes.iterrows():
            rows.append(
                {
                    "name": row.get("gene", gene_name),
                    "log2FoldChange": row.get("log2FoldChange", 0),
                    "pvalue": row.get("pvalue", 1),
                    "padj": row.get("padj", 1),
                }
            )
        return rows

    def _generate_pca(self) -> Path:
        """Generate a PCA plot from the count matrix."""
        out_path = self.plots_dir / "pca.png"
        log_counts = self.counts.select_dtypes(include=[np.number]).apply(np.log1p)
        plotter = PCAPlot(theme=self.theme)
        plotter.plot(
            data=log_counts,
            transpose=True,
            cluster=True,
            n_clusters=min(3, max(1, log_counts.shape[1])),
            title="PCA of Gene Expression",
            output=str(out_path),
        )
        return out_path

    def _generate_volcano(self) -> Path:
        """Generate a volcano plot from differential expression results."""
        out_path = self.plots_dir / "volcano.png"
        de_df = self.de_results.reset_index()
        y_column = "padj" if "padj" in de_df.columns else "pvalue"

        if "log2FoldChange" not in de_df.columns or y_column not in de_df.columns:
            raise RuntimeError("Differential expression results must contain log2FoldChange and pvalue/padj.")

        plotter = VolcanoPlot(theme=self.theme)
        plotter.plot(
            data=de_df,
            x="log2FoldChange",
            y=y_column,
            title="Volcano Plot",
            output=str(out_path),
        )
        return out_path

    def _generate_heatmap(self) -> Path:
        """Generate a heatmap for the most informative genes."""
        out_path = self.plots_dir / "heatmap.png"
        numeric_counts = self.counts.select_dtypes(include=[np.number])

        if numeric_counts.empty:
            raise RuntimeError("Counts matrix must contain numeric columns to generate a heatmap.")

        if "padj" in self.de_results.columns:
            sig_genes = self.de_results[self.de_results["padj"] < 0.05].sort_values("padj").head(50).index
        else:
            sig_genes = pd.Index([])

        if len(sig_genes) < 2:
            sig_genes = numeric_counts.var(axis=1).sort_values(ascending=False).head(50).index

        subset_counts = numeric_counts.loc[sig_genes].apply(np.log1p)
        plotter = HeatmapPlot(theme=self.theme)
        plotter.plot(
            data=subset_counts,
            cluster_rows=True,
            cluster_cols=True,
            z_score=0,
            title="Top DE Genes Heatmap",
            output=str(out_path),
        )
        return out_path

    def _process_gsea_plots(self) -> dict[str, str]:
        """Copy GSEA plots into the report directory and return relative paths."""
        processed_plots: dict[str, str] = {}
        if not self.gsea_plots:
            return processed_plots

        for term, path in self.gsea_plots.items():
            if not path.exists():
                logger.warning("GSEA plot not found at %s", path)
                continue

            dest_name = f"gsea_{path.name}"
            dest_path = self.plots_dir / dest_name
            shutil.copy2(path, dest_path)
            processed_plots[term] = f"plots/{dest_name}"

        return processed_plots
