# bio-analyze-rna-seq

[![codecov](https://codecov.io/gh/497363983/bio-analyze/graph/badge.svg?token=I78TXQBORK&component=rna_seq)](https://codecov.io/gh/497363983/bio-analyze)

**bio-analyze-rna-seq** is the dedicated transcriptome analysis module in the `bio-analyze` toolbox. It provides a fully automated end-to-end pipeline solution from raw sequencing data to the final visualization report.

## ✨ Features

- **Fully Automated Workflow**: One-click execution of all steps from FastQ to HTML report.
- **Flexible Configuration**: Supports command-line arguments as well as JSON/YAML configuration files.
- **Modular Execution**: Supports running specific steps of the analysis pipeline independently (e.g., only running QC or quantification).
- **Auto SRA Download**: Supports direct input of NCBI SRA Accession IDs, automatically downloading and converting data to FASTQ format.
- **Quality Control (QC)**: Uses `FastQC` to generate professional QC reports and integrates `fastp` for efficient data trimming and filtering.
- **Ultra-fast Quantification**: Uses `Salmon` for pseudo-alignment-based transcript quantification, which is extremely fast and accurate.
- **Differential Expression Analysis**: Based on a native Python implementation of `PyDESeq2`, providing robust differential gene screening.
- **Enrichment Analysis**: Automatically performs GO (Gene Ontology) and KEGG pathway enrichment analysis, as well as GSEA (Gene Set Enrichment Analysis) using `GSEApy`.
- **Visualization Report**: Generates an interactive HTML report including PCA plots, volcano plots, heatmaps, enrichment analysis results, and GSEA plots.
- **Auto Reference Genome**: Simply specify the species name (e.g., "Homo sapiens") to automatically download and build the index.

## 🚀 Quick Start

### Scenario 1: Using Local Data

#### 1. Prepare Data

Place all FastQ files (`.fastq.gz` or `.fq.gz`) into a single folder. Both paired-end (`_R1`/`_R2` or `_1`/`_2`) and single-end sequencing data are supported.

#### 2. Prepare Design File

Create a CSV file (e.g., `design.csv`) to define the relationship between samples and experimental conditions. It must contain two columns: `sample` and `condition`:

| sample  | condition |
| :------ | :-------- |
| sample1 | control   |
| sample2 | control   |
| sample3 | treated   |
| sample4 | treated   |

> **Note**: The names in the `sample` column must match the FastQ filenames (excluding the extension and the `_R1`/`_R2` part).

#### 3. Run Analysis

Start the analysis pipeline using the following command:

```bash
uv run bioanalyze rna_seq run \
    --input ./raw_data \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens" \
    --threads 8
```

### Scenario 2: Direct Use of SRA IDs

If you don't have local data, you can directly provide NCBI SRA Accession IDs. The tool will automatically download, convert, and run the analysis.

```bash
uv run bioanalyze rna_seq run \
    --sra-id SRR12345678 \
    --sra-id SRR12345679 \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens"
```

> **Note**: Downloaded data will be saved in the `raw_data` subdirectory under the specified `--output` directory.

### Scenario 3: Using a Configuration File (JSON/YAML)

To simplify long commands, you can write parameters into a configuration file (e.g., `config.yaml`):

```yaml
input_dir: "./raw_data"
output_dir: "./analysis_results"
design_file: "./design.csv"
species: "Homo sapiens"
threads: 8
skip_qc: false

# Advanced QC Configuration (Optional)
qc:
  qualified_quality_phred: 20
  length_required: 30
  dedup: true
```

Then run:

```bash
uv run bioanalyze rna_seq run --config config.yaml
```

### Scenario 4: Step-by-Step Execution

You can use standalone subcommands to run specific steps in the analysis pipeline, providing greater flexibility.

#### 1. Download Data (`download`)
```bash
uv run bioanalyze rna_seq download --sra-id SRR123456 -o ./raw_data
```

#### 2. Prepare Reference Genome (`genome`)
```bash
uv run bioanalyze rna_seq genome -s "Homo sapiens" -o ./reference
# Or specify local files
uv run bioanalyze rna_seq genome --fasta genome.fa --gtf genes.gtf -o ./reference
```

#### 3. Quality Control (`qc`)
```bash
uv run bioanalyze rna_seq qc -i ./raw_data -o ./qc_results
```

#### 4. Alignment (`align`) - Optional
```bash
uv run bioanalyze rna_seq align -i ./qc_results -o ./align_results --fasta ./reference/genome.fa --gtf ./reference/genes.gtf
```

#### 5. Quantification (`quant`)
```bash
uv run bioanalyze rna_seq quant -i ./qc_results -o ./quant_results --fasta ./reference/transcripts.fa
```

#### 6. Differential Expression Analysis (`de`)
```bash
uv run bioanalyze rna_seq de --counts ./quant_results/counts.csv --design design.csv -o ./de_results
```

#### 7. Enrichment Analysis (`enrich`)
```bash
uv run bioanalyze rna_seq enrich --de-results ./de_results/deseq2_results.csv -s "Homo sapiens" -o ./enrich_results
```

## 📋 Command Details

### `run` (Full Pipeline)
Runs the complete RNA-Seq analysis pipeline.

### `download`
Downloads data from NCBI SRA and converts it to FastQ format.
- `--sra-id`: SRA Accession ID.
- `-o, --output`: Output directory.

### `genome`
Prepares the reference genome (downloads or indexes).
- `-s, --species`: Species name.
- `--fasta`: Local FASTA file.
- `--gtf`: Local GTF file.

### `qc`
Runs quality control and trimming.
- `-i, --input`: Input directory.
- `-o, --output`: Output directory.
- `--skip-trim`: Skip trimming.

### `align`
Runs STAR alignment.
- `-i, --input`: Clean reads directory.
- `--fasta`: Genome FASTA.
- `--gtf`: Genome GTF.

### `quant`
Runs Salmon quantification.
- `-i, --input`: Clean reads directory.
- `--fasta`: Transcript/Genome FASTA.

### `de`
Runs DESeq2 differential expression analysis.
- `--counts`: Count matrix CSV.
- `--design`: Design matrix CSV.

### `enrich`
Runs GO/KEGG enrichment analysis.
- `--de-results`: DESeq2 results CSV.
- `-s, --species`: Species name.

### `gsea`
Runs GSEA enrichment analysis.
- `--de-results`: DESeq2 results CSV.
- `-s, --species`: Species name.
- `--gene-sets`: Gene sets library name (Default: KEGG_2021_Human).
- `--ranking-metric`: Ranking metric (Default: auto).

## 📋 `run` Command Parameters Detail

- `-c, --config <FILE>`: **(Optional)** JSON/YAML configuration file path. If provided, parameters in the file will serve as defaults.
- `--step <STR>`: **(Optional)** Run only a specific step (`download`, `reference`, `qc`, `quant`, `de`, `enrichment`, `report`). Runs all steps by default.
- `-i, --input <DIR>`: **(Optional)** Directory path containing raw FastQ files. Mandatory if `--sra-id` is not provided.
- `--sra-id <STR>`: **(Optional)** NCBI SRA Accession ID (e.g., `SRR123456`). Can be used multiple times to specify multiple IDs.
- `-o, --output <DIR>`: **(Mandatory)** Output directory for analysis results.
- `-d, --design <FILE>`: **(Mandatory)** Path to the experimental design CSV file.
- `-s, --species <STR>`: **(Optional)** Species name (e.g., "Homo sapiens", "Mus musculus"). Used for automatic reference genome download and enrichment analysis.
- `--genome-fasta <FILE>`: **(Optional)** Local reference genome FASTA file path (overrides `--species`).
- `--genome-gtf <FILE>`: **(Optional)** Local genome annotation GTF file path (overrides `--species`).
- `-t, --threads <INT>`: **(Optional)** Number of parallel threads (Default: 4).
- `--skip-qc`: Skip the quality control step.
- `--skip-trim`: Skip the trimming step (perform QC only).
- `--star-align`: Enable STAR alignment and generate chromosome distribution plots.
- `--theme <STR>`: Specify the plotting theme (Default: `default`, Options: `nature`, `science`, etc.).

### 🔧 Advanced QC Options

These parameters are passed directly to `fastp` for data cleaning:

- `--qualified-quality-phred <INT>`: Base quality value threshold (Phred). Default 15 (Q15).
- `--unqualified-percent-limit <INT>`: Allowed percentage of low-quality bases (0-100). Default 40 (40%).
- `--n-base-limit <INT>`: Allowed number of N bases. Default 5.
- `--length-required <INT>`: Length filtering threshold; reads shorter than this will be discarded. Default 15.
- `--max-len1 <INT>`: Maximum length limit for Read1; excess parts will be trimmed. Default 0 (no limit).
- `--max-len2 <INT>`: Maximum length limit for Read2; excess parts will be trimmed. Default 0 (no limit).
- `--adapter-sequence <STR>`: Adapter sequence for Read1. Automatically detected if not provided.
- `--adapter-sequence-r2 <STR>`: Adapter sequence for Read2. Automatically detected if not provided.
- `--trim-front1 <INT>`: Number of bases to trim from the 5' end of Read1.
- `--trim-tail1 <INT>`: Number of bases to trim from the 3' end of Read1.
- `--cut-right`: Enable sliding window trimming from the 3' end.
- `--cut-window-size <INT>`: Window size for cut_right. Default 4.
- `--cut-mean-quality <INT>`: Mean quality threshold for cut_right. Default 20.
- `--dedup`: Enable deduplication.
- `--poly-g-min-len <INT>`: Minimum length detection threshold for polyG tail trimming. Default 10.

## 📦 Python API

### 1. Full Pipeline (`RNASeqPipeline`)

```python
from bio_analyze_rna_seq import RNASeqPipeline
from pathlib import Path

pipeline = RNASeqPipeline(
    input_dir=Path("./raw_data"),
    output_dir=Path("./results"),
    design_file=Path("design.csv"),
    species="Homo sapiens",
    threads=8,
    skip_qc=False
)

pipeline.run()
```

### 2. SRA Download (`SRAManager`)

```python
from bio_analyze_rna_seq.sra import SRAManager
from pathlib import Path

manager = SRAManager(output_dir=Path("./raw_data"), threads=4)
manager.download(["SRR123456", "SRR789012"])
```

### 3. Quantification (`QuantManager`)

```python
from bio_analyze_rna_seq.quant import QuantManager
from pathlib import Path

# reads dictionary structure: {sample_name: {"R1": path, "R2": path}}
reads = {
    "sample1": {"R1": "sample1_1.fq.gz", "R2": "sample1_2.fq.gz"}
}
reference = {
    "fasta": Path("genome.fa"),
    "gtf": Path("genes.gtf")
}

manager = QuantManager(
    reads=reads,
    reference=reference,
    output_dir=Path("./quant_results"),
    threads=8
)

# Returns the merged count matrix (DataFrame)
counts_df = manager.run()
```

### 4. Report Generation (`ReportGenerator`)

```python
from bio_analyze_rna_seq.report import ReportGenerator
from pathlib import Path

# Needs results from previous steps
generator = ReportGenerator(
    output_dir=Path("./report"),
    qc_stats=qc_data,          # from QCNode
    counts=counts_df,          # from QuantNode
    de_results=de_df,          # from DENode
    enrich_results=enrich_dict # from EnrichmentNode
)

generator.generate()
```

## ⚙️ Requirements

This module depends on the following external tools. Please ensure they are installed and available in the system PATH:

1. **fastp**: (Required) For data trimming and basic QC.
2. **salmon**: (Required) For quantification.
3. **fastqc**: (Optional) For generating detailed quality control reports. If not installed, only fastp will be used for QC.
4. **STAR**: (Optional) For alignment and chromosome distribution analysis if `--star-align` is enabled.
5. **samtools**: (Optional) For BAM file indexing and statistics if `--star-align` is enabled.
6. **gffread**: (Optional) For extracting transcript sequences if genome FASTA+GTF is provided but transcript FASTA is not.
7. **sra-tools**: (Optional) Required if using the `--sra-id` feature (includes `prefetch` and `fasterq-dump`).

You can quickly install these dependencies via `conda` or `mamba`:

```bash
conda install -c bioconda fastp salmon fastqc star samtools gffread sra-tools
```
