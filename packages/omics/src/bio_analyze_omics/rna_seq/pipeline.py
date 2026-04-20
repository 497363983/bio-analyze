from __future__ import annotations
from pathlib import Path

from bio_analyze_core.logging import get_logger
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

logger = get_logger("bio_analyze_omics.rna_seq")

class RNASeqPipeline:
    """
    Run RNA-Seq Analysis Pipeline.

    Args:
        input_dir (Path, optional):
            Directory containing raw FastQ files.
        output_dir (Path):
            Output directory for analysis results.
        design_file (Path):
            Path to experimental design CSV file.
        species (str, optional):
            Species name (e.g. "Homo sapiens").
        assembly (str, optional):
            Reference assembly accession (e.g. "GCA_013347765.1").
        provider (str, optional):
            Reference genome provider (e.g. "NCBI").
        genome_fasta (Path, optional):
            Path to reference genome FASTA file.
        genome_gtf (Path, optional):
            Path to genome annotation GTF file.
        threads (int, optional):
            Number of parallel threads (default: 4).
        skip_qc (bool, optional):
            Skip quality control steps.
        skip_trim (bool, optional):
            Skip trimming steps.
        sra_ids (list[str], optional):
            List of NCBI SRA Accession IDs.
        step (str, optional):
            Run only specific steps.
        qc_params (dict, optional):
            Additional QC parameters.
        star_align (bool, optional):
            Enable STAR alignment.
        theme (str, optional):
            Plotting theme.
    """

    def __init__(
        self,
        input_dir: Path | None,
        output_dir: Path,
        design_file: Path,
        species: str | None = None,
        assembly: str | None = None,
        provider: str | None = None,
        genome_fasta: Path | None = None,
        genome_gtf: Path | None = None,
        threads: int = 4,
        skip_qc: bool = False,
        skip_trim: bool = False,
        sra_ids: list[str] | None = None,
        step: str | None = None,
        qc_params: dict | None = None,
        quant_tool: str = "salmon",
        quant_compare_tools: list[str] | None = None,
        quant_config: dict | None = None,
        star_align: bool = False,
        theme: str = "default",
    ):
        self.input_dir = Path(input_dir) if input_dir else None
        self.output_dir = Path(output_dir)
        self.design_file = Path(design_file)
        self.species = species
        self.assembly = assembly
        self.provider = provider
        self.genome_fasta = Path(genome_fasta) if genome_fasta else None
        self.genome_gtf = Path(genome_gtf) if genome_gtf else None
        self.threads = threads
        self.skip_qc = skip_qc
        self.skip_trim = skip_trim
        self.sra_ids = sra_ids
        self.step = step
        self.qc_params = qc_params or {}
        self.quant_tool = quant_tool
        self.quant_compare_tools = quant_compare_tools or []
        self.quant_config = quant_config or {}
        self.star_align = star_align
        self.theme = theme

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.input_dir and not self.sra_ids and not self.step:
            raise ValueError("Either input_dir or sra_ids must be provided.")

    def run(self):
        logger.info("Starting RNA-Seq Analysis Pipeline...")

        state_file = self.output_dir / "pipeline_state.json"
        pipeline = Pipeline("RNASeqPipeline", str(state_file))

        # 填充上下文
        pipeline.context.input_dir = self.input_dir
        pipeline.context.output_dir = self.output_dir
        pipeline.context.design_file = self.design_file
        pipeline.context.species = self.species
        pipeline.context.assembly = self.assembly
        pipeline.context.provider = self.provider
        pipeline.context.genome_fasta = self.genome_fasta
        pipeline.context.genome_gtf = self.genome_gtf
        pipeline.context.threads = self.threads
        pipeline.context.skip_qc = self.skip_qc
        pipeline.context.skip_trim = self.skip_trim
        pipeline.context.sra_ids = self.sra_ids
        pipeline.context.step = self.step
        pipeline.context.qc_params = self.qc_params
        pipeline.context.quant_tool = self.quant_tool
        pipeline.context.quant_compare_tools = self.quant_compare_tools
        pipeline.context.quant_config = self.quant_config
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
