from pathlib import Path

import gseapy as gp
import numpy as np
import pandas as pd
from bio_analyze_plot.plots.gsea import GSEAPlot

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)


def calculate_running_es(
    ranked_genes: list[str],
    gene_set: list[str],
    ranking_metrics: np.ndarray,
    weighted_score_type: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    zh: 计算 GSEA 运行富集评分。
    en: Calculate GSEA running enrichment score.

    Args:
        ranked_genes (list[str]):
            zh: 按指标排序的基因名称列表。
            en: List of gene names sorted by metric.
        gene_set (list[str]):
            zh: 目标基因集中的基因列表。
            en: List of genes in the target gene set.
        ranking_metrics (np.ndarray):
            zh: 对应于 ranked_genes 的排序指标数组。
            en: Array of ranking metrics corresponding to ranked_genes.
        weighted_score_type (float, optional):
            zh: 排序指标的权重（默认为 1.0）。
            en: Weight of ranking metric (default is 1.0).

    Returns:
        tuple[np.ndarray, np.ndarray]:
            zh: (running_es_array, hits_boolean_array)
            en: (running_es_array, hits_boolean_array)
    """
    N = len(ranked_genes)
    # 命中的布尔数组
    hits = np.in1d(ranked_genes, gene_set)

    if not np.any(hits):
        return np.zeros(N), hits

    # 计算 P_hit
    # |r|^p
    r_p = np.abs(ranking_metrics) ** weighted_score_type
    # 仅保留命中为 True 的值
    hit_scores = np.where(hits, r_p, 0)
    P_hit = np.cumsum(hit_scores)

    if P_hit[-1] > 0:
        P_hit = P_hit / P_hit[-1]

    # 计算 P_miss
    # 1 / (N - N_h) where miss
    # N_h = hits.sum()
    N_h = hits.sum()
    if N_h == N:
        # 所有基因都命中了？不太可能，但处理一下
        P_miss = np.zeros(N)
    else:
        miss_scores = np.where(~hits, 1 / (N - N_h), 0)
        P_miss = np.cumsum(miss_scores)

    RES = P_hit - P_miss
    return RES, hits


class EnrichmentManager:
    """
    zh: 富集分析管理器。
    en: Enrichment analysis manager.
    """

    def __init__(self, de_results: pd.DataFrame, species: str | None, output_dir: Path, theme: str = "default"):
        """
        zh: 初始化富集分析管理器。
        en: Initialize the enrichment analysis manager.

        Args:
            de_results (pd.DataFrame):
                zh: 差异表达分析结果 DataFrame。
                en: Differential expression analysis results DataFrame.
            species (str | None):
                zh: 物种名称（例如 'Homo sapiens'）。
                en: Species name (e.g., 'Homo sapiens').
            output_dir (Path):
                zh: 输出目录路径。
                en: Path to the output directory.
            theme (str, optional):
                zh: 绘图主题。
                en: Plotting theme.
        """
        self.de_results = de_results
        self.species = species
        self.output_dir = output_dir
        self.theme = theme
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict:
        """
        zh: 运行富集分析 (GO/KEGG)。
        en: Run enrichment analysis (GO/KEGG).

        Returns:
            dict:
                zh: 包含每个库的富集结果的字典。
                en: Dictionary containing enrichment results for each library.
        """
        if not self.species:
            logger.warning("No species provided. Skipping enrichment analysis.")
            return {}

        # 根据需要将物种映射到 gseapy 库名称
        # gseapy 通常可以很好地处理 'Human', 'Mouse'。

        # 过滤显著基因 (padj < 0.05)
        # 确保 padj 不为 NaN
        df_sig = self.de_results.dropna(subset=["padj"])
        sig_genes = df_sig[df_sig["padj"] < 0.05].index.tolist()

        if not sig_genes:
            logger.warning("No significant genes found (padj < 0.05). Skipping enrichment.")
            return {}

        logger.info(f"Running enrichment analysis for {len(sig_genes)} significant genes...")

        results = {}
        libraries = ["GO_Biological_Process_2021", "KEGG_2021_Human"]
        if "mouse" in self.species.lower():
            libraries = ["GO_Biological_Process_2021", "KEGG_2019_Mouse"]

        for lib in libraries:
            try:
                enr = gp.enrichr(
                    gene_list=sig_genes,
                    gene_sets=lib,
                    organism=self.species,  # gseapy 处理物种查找
                    outdir=str(self.output_dir / lib),
                    cutoff=0.05,
                )
                if enr.results.empty:
                    logger.info(f"No enrichment found for {lib}")
                    continue

                results[lib] = enr.results

                # Save plot? Enrichr usually generates bar plots automatically if outdir is set.
                # But we might want to use our own BarPlot later.

            except Exception as e:
                logger.error(f"Enrichment failed for {lib}: {e}")

        return results

    def run_gsea(
        self,
        gene_sets: str | list[str] = "KEGG_2021_Human",
        ranking_metric: str = "auto",
        top_n_plot: int = 5,
        plot_categories: list[str] | None = None,
    ) -> dict[str, Path]:
        """
        zh: 运行 GSEA 分析。
        en: Run GSEA analysis.

        Args:
            gene_sets (str | list[str], optional):
                zh: 基因集库名称（例如 'KEGG_2021_Human'）或基因集列表。
                en: Gene set library name (e.g. 'KEGG_2021_Human') or list of gene sets.
            ranking_metric (str, optional):
                zh: 用于排序的列。'auto' 尝试 'stat'，然后根据 pvalue/log2fc 计算。
                en: Column used for ranking. 'auto' tries 'stat', then calculates from pvalue/log2fc.
            top_n_plot (int, optional):
                zh: 要绘制的顶部通路数量。
                en: Number of top pathways to plot.
            plot_categories (list[str] | None, optional):
                zh: 要绘制的特定类别（术语）。
                en: Specific categories (terms) to plot.

        Returns:
            dict[str, Path]:
                zh: 术语名称到生成的绘图文件路径的映射。
                en: Mapping of term names to generated plot file paths.
        """
        if not self.species:
            logger.warning("No species provided. Skipping GSEA.")
            return {}

        logger.info("Preparing data for GSEA...")
        df = self.de_results.copy()

        # 确定排序指标
        metric_col = None
        if ranking_metric == "auto":
            if "stat" in df.columns:
                metric_col = "stat"
                logger.info("Using 'stat' column for ranking.")
            elif "log2FoldChange" in df.columns and "pvalue" in df.columns:
                # 计算 -log10(pvalue) * sign(log2FC)
                # 处理 pvalue=0 -> 替换为最小正数
                min_pval = df.loc[df["pvalue"] > 0, "pvalue"].min()
                if pd.isna(min_pval):
                    min_pval = 1e-300  # Fallback

                df["pvalue_filled"] = df["pvalue"].replace(0, min_pval / 10)
                df["rank_metric"] = -np.log10(df["pvalue_filled"]) * np.sign(df["log2FoldChange"])
                metric_col = "rank_metric"
                logger.info("Calculated ranking metric from pvalue and log2FoldChange.")
            elif "log2FoldChange" in df.columns:
                metric_col = "log2FoldChange"
                logger.info("Using 'log2FoldChange' column for ranking (fallback).")
            else:
                logger.error("Could not determine ranking metric. GSEA skipped.")
                return {}
        elif ranking_metric in df.columns:
            metric_col = ranking_metric
        else:
            logger.error(f"Ranking metric column '{ranking_metric}' not found.")
            return {}

        # 准备排序列表
        # 删除指标中的 NaN
        df = df.dropna(subset=[metric_col])
        # 降序排序
        df = df.sort_values(by=metric_col, ascending=False)

        # 创建排序序列
        # 索引必须是基因名称
        rnk = df[metric_col]

        # 运行 GSEA
        out_dir = self.output_dir / "GSEA"
        out_dir.mkdir(exist_ok=True)

        # 如果需要，调整小鼠的基因集并提供默认值
        final_gene_sets = gene_sets
        if gene_sets == "KEGG_2021_Human" and "mouse" in self.species.lower():
            final_gene_sets = "KEGG_2019_Mouse"

        logger.info(f"Running GSEA prerank with {final_gene_sets}...")

        generated_plots = {}

        try:
            pre_res = gp.prerank(
                rnk=rnk,
                gene_sets=final_gene_sets,
                threads=4,
                min_size=5,
                max_size=1000,
                permutation_num=1000,
                outdir=str(out_dir),
                seed=42,
                verbose=True,
            )

            if pre_res.res2d.empty:
                logger.warning("GSEA returned no results.")
                return {}

            # 过滤显著结果（fdr < 0.25 是 GSEA 的标准，但我们可以更严格或更宽松）
            # 绘制前 N 个
            res_df = pre_res.res2d.sort_values(by="NES", key=abs, ascending=False)

            # 确定要绘制的术语
            terms_to_plot = []
            if plot_categories:
                terms_to_plot = plot_categories
            else:
                terms_to_plot = res_df.head(top_n_plot).index.tolist()

            logger.info(f"Plotting {len(terms_to_plot)} GSEA plots...")

            plotter = GSEAPlot(theme=self.theme)

            ranked_genes = rnk.index.tolist()
            ranking_metrics = rnk.values

            for term in terms_to_plot:
                if term not in pre_res.results:
                    logger.warning(f"Term '{term}' not found in GSEA results.")
                    continue

                term_res = pre_res.results[term]
                # term_res 通常有 'genes'（输入中集合内的基因列表）
                # 但为了安全起见，让我们从 term_res 获取基因集或重新读取
                # gseapy 结果对象结构：
                # term_res 可能是 dict 或对象。在最近的版本中，pre_res.results[term] 可能是 dict-like 或对象
                # 包含 'genes', 'hits', 'es', 'nes' 等。

                # 获取命中基因（交集）
                # 在 prerank 中，term_res['genes'] 是前缘基因还是所有基因？
                # 实际上如果我们知道基因，我们可以直接使用基因集名称。
                # 但 gseapy 已经做了交集。

                # 安全的方法：从结果中检索基因
                # 注意：结果中的 'genes' 通常按排名排序？还是只是集合？
                # 让我们使用包含排序列表中存在的集合成员的 'genes' 字段。
                # 如果 term_res 是对象 (GSEAResult)
                if hasattr(term_res, "genes"):
                    set_genes = term_res.genes
                elif isinstance(term_res, dict) and "genes" in term_res:
                    set_genes = term_res["genes"]
                else:
                    # 尝试在 res2d 'genes' 列中查找（以 ; 分隔的字符串）
                    if "genes" in res_df.columns:
                        genes_str = res_df.loc[term, "genes"]
                        set_genes = genes_str.split(";")
                    else:
                        logger.warning(f"Could not retrieve genes for term '{term}'. Skipping plot.")
                        continue

                # 计算运行 ES
                res, hits = calculate_running_es(ranked_genes, set_genes, ranking_metrics)

                # 构建绘图数据
                plot_data = pd.DataFrame(
                    {
                        "rank": np.arange(len(ranked_genes)),
                        "running_es": res,
                        "hit": hits.astype(int),
                        "metric": ranking_metrics,
                    }
                )

                # 获取注释统计信息
                nes = res_df.loc[term, "NES"]
                pval = res_df.loc[term, "pval"]
                fdr = res_df.loc[term, "fdr"]

                # 清理文件名的术语名称
                safe_term = term.replace("/", "_").replace(":", "_").replace(" ", "_")
                output_file = out_dir / f"gsea_plot_{safe_term}.png"

                plotter.plot(
                    data=plot_data,
                    rank="rank",
                    score="running_es",
                    hit="hit",
                    metric="metric",
                    title=f"GSEA: {term}",
                    output=str(output_file),
                    nes=nes,
                    pvalue=pval,
                    fdr=fdr,
                )
                generated_plots[term] = output_file

        except Exception as e:
            logger.error(f"GSEA execution failed: {e}")
            import traceback

            logger.error(traceback.format_exc())

        return generated_plots
