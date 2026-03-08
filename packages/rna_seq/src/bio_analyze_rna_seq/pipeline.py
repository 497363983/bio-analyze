from pathlib import Path
import pandas as pd
import shutil

from bio_analyze_core.logging import get_logger, setup_logging

from .genome import GenomeManager
from .qc import QCManager
from .quant import QuantManager
from .de import DEManager
from .enrichment import EnrichmentManager
from .report import ReportGenerator

logger = get_logger("bio_analyze.rna_seq")

class RNASeqPipeline:
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        design_file: Path,
        species: str | None = None,
        genome_fasta: Path | None = None,
        genome_gtf: Path | None = None,
        threads: int = 4,
        skip_qc: bool = False,
        skip_trim: bool = False
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.design_file = Path(design_file)
        self.species = species
        self.genome_fasta = Path(genome_fasta) if genome_fasta else None
        self.genome_gtf = Path(genome_gtf) if genome_gtf else None
        self.threads = threads
        self.skip_qc = skip_qc
        self.skip_trim = skip_trim
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        setup_logging()

    def _check_dependencies(self):
        """检查所需的外部工具。"""
        required_tools = ["fastp", "salmon"]
        missing_tools = []
        
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            msg = f"Missing required external tools: {', '.join(missing_tools)}. Please install them and ensure they are in your PATH."
            logger.error(msg)
            raise RuntimeError(msg)
        
        # 检查可选工具
        if not shutil.which("fastqc"):
            logger.warning("FastQC not found. QC report generation will be skipped, but analysis will proceed using fastp.")
        
        logger.info("External dependencies check completed.")

    def run(self):
        logger.info("Starting RNA-Seq Analysis Pipeline...")
        
        # 0. 检查外部工具
        self._check_dependencies()
        
        # 1. 基因组准备
        logger.info("Step 1: Genome Preparation")
        genome_mgr = GenomeManager(
            species=self.species,
            fasta=self.genome_fasta,
            gtf=self.genome_gtf,
            output_dir=self.output_dir / "reference"
        )
        ref_info = genome_mgr.prepare()
        
        # 2. 质量控制和修剪
        logger.info("Step 2: Quality Control & Trimming")
        qc_mgr = QCManager(
            input_dir=self.input_dir,
            output_dir=self.output_dir / "qc",
            threads=self.threads,
            skip_qc=self.skip_qc,
            skip_trim=self.skip_trim
        )
        clean_reads = qc_mgr.run()
        
        # 3. 定量
        logger.info("Step 3: Quantification")
        quant_mgr = QuantManager(
            reads=clean_reads,
            reference=ref_info,
            output_dir=self.output_dir / "quant",
            threads=self.threads
        )
        counts_matrix = quant_mgr.run()
        
        # 4. 差异表达分析
        logger.info("Step 4: Differential Expression Analysis")
        de_mgr = DEManager(
            counts=counts_matrix,
            design_file=self.design_file,
            output_dir=self.output_dir / "de"
        )
        de_results = de_mgr.run()
        
        # 5. 富集分析
        logger.info("Step 5: Enrichment Analysis")
        enrich_mgr = EnrichmentManager(
            de_results=de_results,
            species=self.species, # 富集分析需要物种信息
            output_dir=self.output_dir / "enrichment"
        )
        enrich_results = enrich_mgr.run()
        
        # 6. 生成报告
        logger.info("Step 6: Generating Report")
        
        # 合并统计信息
        qc_stats = qc_mgr.get_stats()
        quant_stats = quant_mgr.get_stats()
        
        for sample, stat in qc_stats.items():
            if sample in quant_stats:
                stat["mapping_rate"] = f"{quant_stats[sample]:.2f}"
        
        reporter = ReportGenerator(
            output_dir=self.output_dir / "report",
            qc_stats=qc_stats,
            counts=counts_matrix,
            de_results=de_results,
            enrich_results=enrich_results
        )
        reporter.generate()
        
        logger.info("Pipeline completed successfully!")
