from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import gseapy as gp
except ImportError:  # pragma: no cover - optional dependency in many test environments
    gp = None

from bio_analyze_plot.plots.gsea import GSEAPlot

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)


def calculate_running_es(
    ranked_genes: list[str],
    gene_set: list[str],
    ranking_metrics: np.ndarray,
    weighted_score_type: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate the running enrichment score used by GSEA plots."""
    total_genes = len(ranked_genes)
    hits = np.in1d(ranked_genes, gene_set)

    if not np.any(hits):
        return np.zeros(total_genes), hits

    weighted_ranks = np.abs(ranking_metrics) ** weighted_score_type
    hit_scores = np.where(hits, weighted_ranks, 0)
    p_hit = np.cumsum(hit_scores)
    if p_hit[-1] > 0:
        p_hit = p_hit / p_hit[-1]

    hit_count = int(hits.sum())
    if hit_count == total_genes:
        p_miss = np.zeros(total_genes)
    else:
        miss_scores = np.where(~hits, 1 / (total_genes - hit_count), 0)
        p_miss = np.cumsum(miss_scores)

    return p_hit - p_miss, hits


class EnrichmentManager:
    """Manager for GO/KEGG enrichment analysis and GSEA plotting."""

    def __init__(self, de_results: pd.DataFrame, species: str | None, output_dir: Path, theme: str = "default"):
        self.de_results = de_results
        self.species = species
        self.output_dir = output_dir
        self.theme = theme
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict[str, Path]:
        """Run over-representation enrichment analysis and persist result tables."""
        if not self.species:
            logger.warning("No species provided. Skipping enrichment analysis.")
            return {}
        if gp is None:
            logger.warning("gseapy is not installed. Skipping enrichment analysis.")
            return {}

        genes = self._select_gene_list()
        if not genes:
            logger.warning("No genes available for enrichment analysis.")
            return {}

        organism = self._infer_organism()
        gene_sets = self._default_gene_sets()
        enrich_dir = self.output_dir / "enrichr"
        enrich_dir.mkdir(exist_ok=True)

        outputs: dict[str, Path] = {}
        for gene_set in gene_sets:
            try:
                logger.info("Running enrichment with %s for %s", gene_set, organism)
                result = gp.enrichr(
                    gene_list=genes,
                    gene_sets=gene_set,
                    organism=organism,
                    outdir=str(enrich_dir / gene_set),
                    no_plot=True,
                )
            except Exception as exc:  # pragma: no cover - depends on external services/data
                logger.error("Enrichment failed for %s: %s", gene_set, exc)
                continue

            raw_result_table = getattr(result, "results", [])
            result_table = (
                raw_result_table
                if isinstance(raw_result_table, pd.DataFrame)
                else pd.DataFrame(raw_result_table)
            )
            if result_table.empty:
                logger.warning("Enrichment returned no rows for %s", gene_set)
                continue

            output_file = enrich_dir / f"{gene_set}.csv"
            result_table.to_csv(output_file, index=False)
            outputs[gene_set] = output_file

        return outputs

    def run_gsea(
        self,
        gene_sets: str | list[str] = "KEGG_2021_Human",
        ranking_metric: str = "auto",
        top_n_plot: int = 5,
        plot_categories: list[str] | None = None,
    ) -> dict[str, Path]:
        """Run GSEA prerank analysis and generate GSEA plots for top terms."""
        if not self.species:
            logger.warning("No species provided. Skipping GSEA.")
            return {}
        if gp is None:
            logger.warning("gseapy is not installed. Skipping GSEA.")
            return {}

        logger.info("Preparing data for GSEA...")
        ranked_frame = self.de_results.copy()
        metric_col = self._resolve_ranking_metric(ranked_frame, ranking_metric)
        if metric_col is None:
            return {}

        ranked_frame = ranked_frame.dropna(subset=[metric_col]).sort_values(by=metric_col, ascending=False)
        ranking_series = ranked_frame[metric_col]

        gsea_dir = self.output_dir / "GSEA"
        gsea_dir.mkdir(exist_ok=True)

        final_gene_sets: str | list[str] = gene_sets
        if isinstance(gene_sets, str) and gene_sets == "KEGG_2021_Human" and "mouse" in self.species.lower():
            final_gene_sets = "KEGG_2019_Mouse"

        logger.info("Running GSEA prerank with %s", final_gene_sets)
        generated_plots: dict[str, Path] = {}

        try:
            pre_res = gp.prerank(
                rnk=ranking_series,
                gene_sets=final_gene_sets,
                threads=4,
                min_size=5,
                max_size=1000,
                permutation_num=1000,
                outdir=str(gsea_dir),
                seed=42,
                verbose=True,
            )
        except Exception as exc:  # pragma: no cover - external runtime behavior
            logger.error("GSEA execution failed: %s", exc)
            return {}

        if pre_res.res2d.empty:
            logger.warning("GSEA returned no results.")
            return {}

        result_frame = pre_res.res2d.sort_values(by="NES", key=abs, ascending=False)
        terms_to_plot = plot_categories or result_frame.head(top_n_plot).index.tolist()
        plotter = GSEAPlot(theme=self.theme)
        ranked_genes = ranking_series.index.tolist()
        ranking_metrics = ranking_series.values

        for term in terms_to_plot:
            term_result = pre_res.results.get(term)
            if term_result is None:
                logger.warning("Term '%s' not found in GSEA results.", term)
                continue

            set_genes = self._extract_term_genes(term_result, result_frame, term)
            if not set_genes:
                logger.warning("Could not retrieve genes for term '%s'.", term)
                continue

            running_es, hits = calculate_running_es(ranked_genes, set_genes, ranking_metrics)
            plot_data = pd.DataFrame(
                {
                    "rank": np.arange(len(ranked_genes)),
                    "running_es": running_es,
                    "hit": hits.astype(int),
                    "metric": ranking_metrics,
                }
            )

            safe_term = term.replace("/", "_").replace(":", "_").replace(" ", "_")
            output_file = gsea_dir / f"gsea_plot_{safe_term}.png"
            plotter.plot(
                data=plot_data,
                rank="rank",
                score="running_es",
                hit="hit",
                metric="metric",
                title=f"GSEA: {term}",
                output=str(output_file),
                nes=result_frame.loc[term, "NES"],
                pvalue=result_frame.loc[term, "pval"],
                fdr=result_frame.loc[term, "fdr"],
            )
            generated_plots[term] = output_file

        return generated_plots

    def _default_gene_sets(self) -> list[str]:
        if not self.species:
            return ["GO_Biological_Process_2021", "KEGG_2021_Human"]
        if "mouse" in self.species.lower():
            return ["GO_Biological_Process_2021", "KEGG_2019_Mouse"]
        return ["GO_Biological_Process_2021", "KEGG_2021_Human"]

    def _infer_organism(self) -> str:
        if not self.species:
            return "Human"
        lowered = self.species.lower()
        if "mouse" in lowered or "mus musculus" in lowered:
            return "Mouse"
        return "Human"

    def _select_gene_list(self) -> list[str]:
        frame = self.de_results.copy()
        if "padj" in frame.columns:
            frame = frame[frame["padj"].fillna(1.0) < 0.05]
        if frame.empty:
            frame = self.de_results
        return [str(gene) for gene in frame.index.tolist() if str(gene)]

    def _resolve_ranking_metric(self, frame: pd.DataFrame, ranking_metric: str) -> str | None:
        if ranking_metric != "auto":
            if ranking_metric in frame.columns:
                return ranking_metric
            logger.error("Ranking metric column '%s' not found.", ranking_metric)
            return None

        if "stat" in frame.columns:
            logger.info("Using 'stat' column for ranking.")
            return "stat"

        if "log2FoldChange" in frame.columns and "pvalue" in frame.columns:
            min_pval = frame.loc[frame["pvalue"] > 0, "pvalue"].min()
            if pd.isna(min_pval):
                min_pval = 1e-300
            frame["pvalue_filled"] = frame["pvalue"].replace(0, min_pval / 10)
            frame["rank_metric"] = -np.log10(frame["pvalue_filled"]) * np.sign(frame["log2FoldChange"])
            logger.info("Calculated ranking metric from pvalue and log2FoldChange.")
            return "rank_metric"

        if "log2FoldChange" in frame.columns:
            logger.info("Using 'log2FoldChange' column for ranking.")
            return "log2FoldChange"

        logger.error("Could not determine ranking metric. GSEA skipped.")
        return None

    def _extract_term_genes(self, term_result: Any, result_frame: pd.DataFrame, term: str) -> list[str]:
        if hasattr(term_result, "genes"):
            return list(term_result.genes)
        if isinstance(term_result, dict) and "genes" in term_result:
            genes = term_result["genes"]
            return list(genes) if isinstance(genes, list) else str(genes).split(";")
        if "genes" in result_frame.columns:
            genes_str = result_frame.loc[term, "genes"]
            return [] if pd.isna(genes_str) else str(genes_str).split(";")
        return []
