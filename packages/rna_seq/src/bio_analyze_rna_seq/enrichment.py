from pathlib import Path
import pandas as pd
import gseapy as gp

from bio_analyze_core.logging import get_logger

logger = get_logger(__name__)

class EnrichmentManager:
    def __init__(self, de_results: pd.DataFrame, species: str | None, output_dir: Path):
        self.de_results = de_results
        self.species = species
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self) -> dict:
        if not self.species:
            logger.warning("No species provided. Skipping enrichment analysis.")
            return {}
            
        # 根据需要将物种映射到 gseapy 库名称
        # gseapy 通常可以很好地处理 'Human', 'Mouse'。
        
        # 过滤显著基因 (padj < 0.05)
        sig_genes = self.de_results[self.de_results["padj"] < 0.05].index.tolist()
        
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
                    organism=self.species, # gseapy 处理物种查找
                    outdir=str(self.output_dir / lib),
                    cutoff=0.05
                )
                if enr.results.empty:
                    logger.info(f"No enrichment found for {lib}")
                    continue
                    
                results[lib] = enr.results
                
            except Exception as e:
                logger.error(f"Enrichment failed for {lib}: {e}")
                
        return results
