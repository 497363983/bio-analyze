import shutil

import pandas as pd

from bio_analyze_core.pipeline import Context, Node, Progress

from .align import StarAlignmentManager
from .de import DEManager
from .enrichment import EnrichmentManager
from .genome import GenomeManager
from .qc import QCManager
from .quant import QuantManager
from .report import ReportGenerator
from .sra import SRAManager


class CheckDependenciesNode(Node):
    """
    zh: 检查外部依赖工具节点。
    en: Node to check for external dependency tools.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行依赖检查。
        en: Execute dependency check.

        Args:
            context (Context):
                zh: 流转上下文。
                en: Execution context.
            progress (Progress):
                zh: 进度管理器。
                en: Progress manager.
            logger (Logger):
                zh: 日志记录器。
                en: Logger instance.
        """
        step = context.get("step")
        star_align = context.get("star_align", False)

        required_tools = []
        if not step or step in ["qc", "trim"]:
            required_tools.append("fastp")
        if not step or step == "quant":
            required_tools.append("salmon")
        if step == "align" or (star_align and not step):
            required_tools.extend(["STAR", "samtools"])

        missing_tools = []
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)

        if missing_tools:
            msg = f"Missing required external tools for step '{step or 'all'}': {', '.join(missing_tools)}. Please install them and ensure they are in your PATH."
            logger.error(msg)
            raise RuntimeError(msg)

        # Check optional tools
        if (not step or step == "qc") and not shutil.which("fastqc"):
            logger.warning(
                "FastQC not found. QC report generation will be skipped, but analysis will proceed using fastp."
            )

        if (
            context.get("sra_ids")
            and (not step or step == "download")
            and (not shutil.which("prefetch") or not shutil.which("fasterq-dump"))
        ):
            logger.error("sra-tools (prefetch, fasterq-dump) not found, but sra_ids provided.")
            raise RuntimeError("sra-tools required for SRA download.")

        logger.info("External dependencies check completed.")


class SRADownloadNode(Node):
    """
    zh: SRA 数据下载节点。
    en: SRA data download node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行 SRA 数据下载。
        en: Execute SRA data download.
        """
        if context.get("sra_ids"):
            logger.info("Downloading SRA Data")
            sra_dir = context.output_dir / "raw_data"
            sra_mgr = SRAManager(output_dir=sra_dir, threads=context.threads)

            # Check for existing progress
            downloaded_sra_ids = context.get("downloaded_sra_ids", [])
            remaining_sra_ids = [sra for sra in context.sra_ids if sra not in downloaded_sra_ids]

            if remaining_sra_ids:
                logger.info(
                    f"Resuming download. Remaining: {len(remaining_sra_ids)}, Completed: {len(downloaded_sra_ids)}"
                )

                # We need to process one by one to support checkpointing
                total_sra = len(context.sra_ids)
                current_completed = len(downloaded_sra_ids)
                
                for i, sra_id in enumerate(remaining_sra_ids):
                    logger.info(f"Processing {sra_id}...")
                    
                    progress.update(
                        f"Downloading {sra_id} ({current_completed + i + 1}/{total_sra})",
                        percentage=((current_completed + i + 1) / total_sra) * 100
                    )
                    
                    sra_mgr.process_single_sra(sra_id)

                    downloaded_sra_ids.append(sra_id)
                    context.downloaded_sra_ids = downloaded_sra_ids
                    context.checkpoint()
            else:
                logger.info("All SRA downloads completed.")

            # Update input_dir to point to downloaded files
            context.input_dir = sra_dir

        if not context.input_dir or not context.input_dir.exists():
            raise RuntimeError(f"Input directory {context.input_dir} does not exist or was not created.")


class GenomePrepNode(Node):
    """
    zh: 基因组准备节点。
    en: Genome preparation node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行基因组准备。
        en: Execute genome preparation.
        """
        logger.info("Genome Preparation")
        genome_mgr = GenomeManager(
            species=context.species,
            fasta=context.genome_fasta,
            gtf=context.genome_gtf,
            output_dir=context.output_dir / "reference",
        )
        ref_info = genome_mgr.prepare()
        context.ref_info = ref_info


class QCNode(Node):
    """
    zh: 质量控制节点。
    en: Quality control node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行质量控制和修剪。
        en: Execute quality control and trimming.
        """
        logger.info("Quality Control & Trimming")
        qc_mgr = QCManager(
            input_dir=context.input_dir,
            output_dir=context.output_dir / "qc",
            threads=context.threads,
            skip_qc=context.skip_qc,
            skip_trim=context.skip_trim,
            **context.qc_params,
        )
        clean_reads = qc_mgr.run()
        context.clean_reads = clean_reads


class StarAlignNode(Node):
    """
    zh: STAR 比对节点。
    en: STAR alignment node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行 STAR 比对。
        en: Execute STAR alignment.
        """
        logger.info("STAR Alignment & Chromosome Distribution")

        ref_info = context.get("ref_info")
        clean_reads = context.get("clean_reads")

        # Try to recover ref_info if missing
        if not ref_info:
            ref_dir = context.output_dir / "reference"
            if not ref_dir.exists():
                logger.warning("Reference directory not found for STAR alignment.")
            else:
                ref_info = {}
                if context.species:
                    genome_path = ref_dir / context.species
                    fastas = list(genome_path.glob("*.fa")) + list(genome_path.glob("*.fasta"))
                    gtfs = list(genome_path.glob("*.gtf"))
                    if fastas:
                        ref_info["fasta"] = fastas[0]
                    if gtfs:
                        ref_info["gtf"] = gtfs[0]
                elif context.genome_fasta:
                    ref_info["fasta"] = context.genome_fasta
                    if context.genome_gtf:
                        ref_info["gtf"] = context.genome_gtf
                context.ref_info = ref_info

        # Try to recover clean_reads if missing
        if not clean_reads:
            qc_dir = context.output_dir / "qc"
            if qc_dir.exists():
                temp_qc_mgr = QCManager(qc_dir, qc_dir)
                all_files = temp_qc_mgr._detect_files(qc_dir)
                clean_reads = {}
                for sample, files in all_files.items():
                    if "clean" in sample:
                        real_sample = sample.replace("_clean", "")
                        clean_reads[real_sample] = files
                if not clean_reads and all_files:
                    clean_reads = all_files
                context.clean_reads = clean_reads

        if ref_info and ref_info.get("fasta") and clean_reads:
            align_mgr = StarAlignmentManager(
                reads=clean_reads,
                reference=ref_info,
                output_dir=context.output_dir / "align",
                threads=context.threads,
                theme=context.theme,
            )
            align_mgr.run()
        else:
            logger.warning("Skipping STAR alignment: missing reference FASTA or clean reads.")


class QuantNode(Node):
    """
    zh: 定量节点。
    en: Quantification node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行 Salmon 定量。
        en: Execute Salmon quantification.
        """
        logger.info("Quantification")

        ref_info = context.get("ref_info")
        clean_reads = context.get("clean_reads")

        # Recover ref_info
        if not ref_info:
            ref_dir = context.output_dir / "reference"
            if not ref_dir.exists():
                logger.warning("Reference directory not found. Assuming genome prep needed but skipped.")

            ref_info = {}
            if context.species:
                genome_path = ref_dir / context.species
                fastas = list(genome_path.glob("*.fa")) + list(genome_path.glob("*.fasta"))
                gtfs = list(genome_path.glob("*.gtf"))
                if fastas:
                    ref_info["fasta"] = fastas[0]
                if gtfs:
                    ref_info["gtf"] = gtfs[0]
            elif context.genome_fasta:
                ref_info["fasta"] = context.genome_fasta
                if context.genome_gtf:
                    ref_info["gtf"] = context.genome_gtf
            context.ref_info = ref_info

        # Recover clean_reads
        if not clean_reads:
            qc_dir = context.output_dir / "qc"
            if qc_dir.exists():
                temp_qc_mgr = QCManager(qc_dir, qc_dir)
                all_files = temp_qc_mgr._detect_files(qc_dir)
                clean_reads = {}
                for sample, files in all_files.items():
                    if "clean" in sample:
                        real_sample = sample.replace("_clean", "")
                        clean_reads[real_sample] = files
                if not clean_reads and all_files:
                    clean_reads = all_files
                context.clean_reads = clean_reads

        if clean_reads:
            quant_mgr = QuantManager(
                reads=clean_reads,
                reference=ref_info,
                output_dir=context.output_dir / "quant",
                threads=context.threads,
            )
            counts_matrix = quant_mgr.run()
            context.counts_matrix = counts_matrix
        else:
            logger.error("No clean reads found for quantification. Please run 'qc' step first.")


class DENode(Node):
    """
    zh: 差异表达分析节点。
    en: Differential expression analysis node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行差异表达分析。
        en: Execute differential expression analysis.
        """
        logger.info("Differential Expression Analysis")

        counts_matrix = context.get("counts_matrix")

        if counts_matrix is None:
            counts_path = context.output_dir / "quant" / "counts.csv"
            if counts_path.exists():
                counts_matrix = pd.read_csv(counts_path, index_col=0)
                context.counts_matrix = counts_matrix

        if counts_matrix is not None:
            de_mgr = DEManager(
                counts=counts_matrix,
                design_file=context.design_file,
                output_dir=context.output_dir / "de",
                theme=context.theme,
            )
            de_results = de_mgr.run()
            context.de_results = de_results


class EnrichmentNode(Node):
    """
    zh: 富集分析节点。
    en: Enrichment analysis node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行富集分析。
        en: Execute enrichment analysis.
        """
        logger.info("Enrichment Analysis")

        de_results = context.get("de_results")

        if de_results is None:
            de_path = context.output_dir / "de" / "deseq2_results.csv"
            if de_path.exists():
                de_results = pd.read_csv(de_path, index_col=0)
                context.de_results = de_results

        if de_results is not None:
            enrich_mgr = EnrichmentManager(
                de_results=de_results,
                species=context.species,
                output_dir=context.output_dir / "enrichment",
                theme=context.theme,
            )
            enrich_results = enrich_mgr.run()
            context.enrich_results = enrich_results

            # Run GSEA
            gsea_plots = enrich_mgr.run_gsea(
                gene_sets="KEGG_2021_Human",  # Should probably be configurable or match EnrichmentManager defaults
                top_n_plot=5,
            )
            context.gsea_plots = gsea_plots


class ReportNode(Node):
    """
    zh: 报告生成节点。
    en: Report generation node.
    """

    def run(self, context: Context, progress: Progress, logger):
        """
        zh: 执行报告生成。
        en: Execute report generation.
        """
        logger.info("Generating Report")

        counts_matrix = context.get("counts_matrix")
        if counts_matrix is None:
            counts_path = context.output_dir / "quant" / "counts.csv"
            if counts_path.exists():
                counts_matrix = pd.read_csv(counts_path, index_col=0)

        de_results = context.get("de_results")
        if de_results is None:
            de_path = context.output_dir / "de" / "deseq2_results.csv"
            if de_path.exists():
                de_results = pd.read_csv(de_path, index_col=0)

        enrich_results = context.get("enrich_results", {})
        gsea_plots = context.get("gsea_plots", {})

        # QC Stats placeholder as in original code
        qc_stats = {}

        if counts_matrix is not None and de_results is not None:
            reporter = ReportGenerator(
                output_dir=context.output_dir / "report",
                qc_stats=qc_stats,
                counts=counts_matrix,
                de_results=de_results,
                enrich_results=enrich_results,
                gsea_plots=gsea_plots,
                theme=context.theme,
            )
            reporter.generate()
