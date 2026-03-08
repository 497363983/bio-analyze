from __future__ import annotations

from pathlib import Path
import typer
from .pipeline import RNASeqPipeline

def get_app() -> typer.Typer:
    app = typer.Typer(help="Transcriptomics analysis workflow.")

    @app.command("run")
    def run_analysis(
        input_dir: Path = typer.Option(
            ..., "--input", "-i", 
            help="Directory containing raw FastQ files."
        ),
        output_dir: Path = typer.Option(
            ..., "--output", "-o", 
            help="Directory for analysis results."
        ),
        design_file: Path = typer.Option(
            ..., "--design", "-d",
            help="CSV file describing experimental design (columns: sample, condition, ...)."
        ),
        species: str = typer.Option(
            None, "--species", "-s",
            help="Species name for auto-downloading reference genome (e.g. 'Homo sapiens')."
        ),
        genome_fasta: Path = typer.Option(
            None, "--genome-fasta",
            help="Path to reference genome FASTA file (overrides --species)."
        ),
        genome_gtf: Path = typer.Option(
            None, "--genome-gtf",
            help="Path to reference genome GTF annotation file (overrides --species)."
        ),
        threads: int = typer.Option(
            4, "--threads", "-t",
            help="Number of threads to use."
        ),
        skip_qc: bool = typer.Option(
            False, "--skip-qc",
            help="Skip Quality Control step."
        ),
        skip_trim: bool = typer.Option(
            False, "--skip-trim",
            help="Skip Trimming step."
        )
    ) -> None:
        """
        运行完整的 RNA-Seq 分析流程。
        """
        pipeline = RNASeqPipeline(
            input_dir=input_dir,
            output_dir=output_dir,
            design_file=design_file,
            species=species,
            genome_fasta=genome_fasta,
            genome_gtf=genome_gtf,
            threads=threads,
            skip_qc=skip_qc,
            skip_trim=skip_trim
        )
        pipeline.run()

    return app
