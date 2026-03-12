from pathlib import Path

from bio_analyze_core.logging import get_logger, setup_logging
from bio_analyze_core.pipeline import Pipeline

from .nodes import (
    CheckDependenciesNode,
    DENode,
    EnrichmentNode,
    GenomePrepNode,
    QCNode,
    QuantNode,
    ReportNode,
    SRADownloadNode,
    StarAlignNode,
)

logger = get_logger("bio_analyze.rna_seq")


class RNASeqPipeline:
    def __init__(
        self,
        input_dir: Path | None,
        output_dir: Path,
        design_file: Path,
        species: str | None = None,
        genome_fasta: Path | None = None,
        genome_gtf: Path | None = None,
        threads: int = 4,
        skip_qc: bool = False,
        skip_trim: bool = False,
        sra_ids: list[str] | None = None,
        step: str | None = None,
        qc_params: dict | None = None,
        star_align: bool = False,
        theme: str = "default",
    ):
        self.input_dir = Path(input_dir) if input_dir else None
        self.output_dir = Path(output_dir)
        self.design_file = Path(design_file)
        self.species = species
        self.genome_fasta = Path(genome_fasta) if genome_fasta else None
        self.genome_gtf = Path(genome_gtf) if genome_gtf else None
        self.threads = threads
        self.skip_qc = skip_qc
        self.skip_trim = skip_trim
        self.sra_ids = sra_ids
        self.step = step
        self.qc_params = qc_params or {}
        self.star_align = star_align
        self.theme = theme

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.input_dir and not self.sra_ids and not self.step:
            raise ValueError("Either input_dir or sra_ids must be provided.")

        # 设置日志
        setup_logging()

    def run(self):
        logger.info("Starting RNA-Seq Analysis Pipeline...")

        state_file = self.output_dir / "pipeline_state.json"
        pipeline = Pipeline("RNASeqPipeline", str(state_file))

        # 填充上下文
        pipeline.context.input_dir = self.input_dir
        pipeline.context.output_dir = self.output_dir
        pipeline.context.design_file = self.design_file
        pipeline.context.species = self.species
        pipeline.context.genome_fasta = self.genome_fasta
        pipeline.context.genome_gtf = self.genome_gtf
        pipeline.context.threads = self.threads
        pipeline.context.skip_qc = self.skip_qc
        pipeline.context.skip_trim = self.skip_trim
        pipeline.context.sra_ids = self.sra_ids
        pipeline.context.step = self.step
        pipeline.context.qc_params = self.qc_params
        pipeline.context.star_align = self.star_align
        pipeline.context.theme = self.theme

        # 添加节点
        pipeline.add_node(CheckDependenciesNode("check_dependencies"))

        if not self.step or self.step == "download":
            pipeline.add_node(SRADownloadNode("sra_download"))

        if not self.step or self.step == "reference":
            pipeline.add_node(GenomePrepNode("genome_prep"))

        if not self.step or self.step == "qc":
            pipeline.add_node(QCNode("qc"))

        # 如果显式请求 STAR 比对，或者未指定步骤且 star_align 为 True，则运行 STAR 比对
        if self.step == "align" or (not self.step and self.star_align):
            pipeline.add_node(StarAlignNode("star_align"))

        if not self.step or self.step == "quant":
            pipeline.add_node(QuantNode("quant"))

        if not self.step or self.step == "de":
            pipeline.add_node(DENode("de"))

        if not self.step or self.step == "enrichment":
            pipeline.add_node(EnrichmentNode("enrichment"))

        if not self.step or self.step == "report":
            pipeline.add_node(ReportNode("report"))

        pipeline.run()

        logger.info("Pipeline completed successfully!")
