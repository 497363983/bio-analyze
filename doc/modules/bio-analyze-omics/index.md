---
---

# bio-analyze-omics

Omics module currently providing the RNA-Seq analysis workflow.

## ✨ Core Features

- **Automated Workflow**: One-click completion from raw data QC, alignment, quantification to differential expression analysis.
- **Reproducibility**: Parameterized configuration management ensures every analysis is traceable.
- **Rich Reports**: Automatically generates HTML quality control reports and interactive charts (Volcano Plot, Heatmap, PCA, GSEA).
- **Tool Integration**: Built-in best practice tools (FastQC, Trimmomatic, STAR/Salmon, DESeq2).

## RNA-Seq Subcommands

- [run](./run.md): Run the complete `bioanalyze omics rna_seq run` pipeline.
- [download](./download.md): Download FASTQ files from SRA.
- [genome](./genome.md): Download reference genome.
- [qc](./qc.md): Quality control of FASTQ files.
- [align](./align.md): Align reads to reference genome.
- [quant](./quant.md): Quantify transcript expression.
- [de](./de.md): Differential expression analysis.
- [enrich](./enrich.md): GO/KEGG enrichment analysis.
- [gsea](./gsea.md): GSEA enrichment analysis.

## ⚙️ Requirements

This module depends on the following external tools, please ensure they are installed and available in the system PATH:

1. **fastp**: (Required) Used for data trimming and basic QC.
2. **salmon**: (Required) Used for quantification.
3. **fastqc**: (Optional) Used for generating detailed quality control reports. If not installed, only fastp will be used for QC.
4. **STAR**: (Optional) Used for alignment and chromosome distribution analysis if `--star-align` is enabled.
5. **samtools**: (Optional) Used for BAM file indexing and statistics if `--star-align` is enabled.
6. **gffread**: (Optional) Used to extract transcript sequences if genome FASTA+GTF are provided but no transcript FASTA.
7. **sra-tools**: (Optional) Must be installed (includes `prefetch` and `fasterq-dump`) if using `--sra-id` feature.
