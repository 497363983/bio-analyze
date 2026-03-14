# bio-analyze-rna-seq

**bio-analyze-rna-seq** is a dedicated transcriptome analysis module in the `bio-analyze` toolkit. It provides an automated full-process solution from raw sequencing data to final visualization reports.

## ✨ Core Features (Features)

- **Fully Automated Workflow**: One-click completion of all steps from FastQ to HTML report.
- **Flexible Configuration**: Supports command-line arguments as well as parameter management via JSON/YAML configuration files.
- **Modular Execution**: Supports running specific steps in the analysis pipeline individually (e.g., running only QC or quantification).
- **Automatic SRA Download**: Supports direct input of NCBI SRA Accession IDs, automatically downloading data and converting to FASTQ format.
- **Quality Control (QC)**: Uses `FastQC` to generate professional QC reports and integrates `fastp` for efficient data trimming and filtering.
- **Ultra-fast Quantification**: Uses `Salmon` for transcript quantification based on Pseudo-alignment, which is extremely fast and accurate.
- **Differential Expression Analysis**: Based on native Python implementation of `PyDESeq2`, providing robust differential gene screening.
- **Enrichment Analysis**: Uses `GSEApy` to automatically perform GO (Gene Ontology) and KEGG pathway enrichment analysis, as well as GSEA (Gene Set Enrichment Analysis).
- **Visualization Report**: Generates interactive HTML reports containing PCA plots, Volcano plots, Heatmaps, enrichment analysis results, and GSEA enrichment plots.
- **Automatic Reference Genome**: Just specify the species name (e.g., "Homo sapiens") to automatically download and build indexes.

## 🚀 Quick Start (Usage)

### Scenario 1: Using Local Data

#### 1. Prepare Data

Place all FastQ files (`.fastq.gz` or `.fq.gz`) in a folder. Supports paired-end (`_R1`/`_R2` or `_1`/`_2`) and single-end sequencing data.

#### 2. Prepare Design File

Create a CSV file (e.g., `design.csv`) defining the relationship between samples and experimental conditions. Must contain `sample` and `condition` columns:

| sample  | condition |
| :------ | :-------- |
| sample1 | control   |
| sample2 | control   |
| sample3 | treated   |
| sample4 | treated   |

> **Note**: The names in the `sample` column must correspond to the FastQ filenames (excluding suffix and `_R1`/`_R2` parts).

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

### Scenario 2: Directly Using SRA ID

If you don't have local data, you can directly provide NCBI SRA Accession IDs, and the tool will automatically download, convert, and run the analysis.

```bash
uv run bioanalyze rna_seq run \
    --sra-id SRR12345678 \
    --sra-id SRR12345679 \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens"
```

> **Note**: Downloaded data will be saved in the `raw_data` subdirectory under the directory specified by `--output`.

### Scenario 3: Using Configuration File (JSON/YAML)

To simplify long command lines, you can write parameters into a configuration file (e.g., `config.yaml`):

```yaml
input_dir: "./raw_data"
output_dir: "./analysis_results"
design_file: "./design.csv"
species: "Homo sapiens"
threads: 8
skip_qc: false

# Advanced QC configuration (optional)
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

You can use independent subcommands to run specific steps in the analysis pipeline, providing greater flexibility.

#### 1. Download Data (download)
```bash
uv run bioanalyze rna_seq download --sra-id SRR123456 -o ./raw_data
```

#### 2. Prepare Reference Genome (genome)
```bash
uv run bioanalyze rna_seq genome -s "Homo sapiens" -o ./reference
# Or specify local files
uv run bioanalyze rna_seq genome --fasta genome.fa --gtf genes.gtf -o ./reference
```

#### 3. Quality Control (qc)
```bash
uv run bioanalyze rna_seq qc -i ./raw_data -o ./qc_results
```

#### 4. Alignment (align) - Optional
```bash
uv run bioanalyze rna_seq align -i ./qc_results -o ./align_results --fasta ./reference/genome.fa --gtf ./reference/genes.gtf
```

#### 5. Quantification (quant)
```bash
uv run bioanalyze rna_seq quant -i ./qc_results -o ./quant_results --fasta ./reference/transcripts.fa
```

#### 6. Differential Expression Analysis (de)
```bash
uv run bioanalyze rna_seq de --counts ./quant_results/counts.csv --design design.csv -o ./de_results
```

#### 7. Enrichment Analysis (enrich)
```bash
uv run bioanalyze rna_seq enrich --de-results ./de_results/deseq2_results.csv -s "Homo sapiens" -o ./enrich_results
```

## 📋 Command Details (Commands)

### `run` (Full Workflow)
Run the complete RNA-Seq analysis pipeline.

### `download`
Download data from NCBI SRA and convert to FastQ format.
- `--sra-id`: SRA Accession ID.
- `-o, --output`: Output directory.

### `genome`
Prepare reference genome (download or index).
- `-s, --species`: Species name.
- `--fasta`: Local FASTA file.
- `--gtf`: Local GTF file.

### `qc`
Run QC and trimming.
- `-i, --input`: Input directory.
- `-o, --output`: Output directory.
- `--skip-trim`: Skip trimming.

### `align`
Run STAR alignment.
- `-i, --input`: Clean reads directory.
- `--fasta`: Genome FASTA.
- `--gtf`: Genome GTF.

### `quant`
Run Salmon quantification.
- `-i, --input`: Clean reads directory.
- `--fasta`: Transcript/Genome FASTA.

### `de`
Run DESeq2 differential expression analysis.
- `--counts`: Counts matrix CSV.
- `--design`: Design matrix CSV.

### `enrich`
Run GO/KEGG enrichment analysis.
- `--de-results`: DESeq2 results CSV.
- `-s, --species`: Species name.

### `gsea`
Run GSEA enrichment analysis.
- `--de-results`: DESeq2 results CSV.
- `-s, --species`: Species name.
- `--gene-sets`: Gene set library name (default: KEGG_2021_Human).
- `--ranking-metric`: Ranking metric (default: auto).

## 📋 run Command Parameter Details

- `-c, --config <FILE>`: **(Optional)** JSON/YAML configuration file path. If provided, parameters in the file will be used as defaults.
- `--step <STR>`: **(Optional)** Run only specific steps (`download`, `reference`, `qc`, `quant`, `de`, `enrichment`, `report`). Default runs all steps.
- `-i, --input <DIR>`: **(Optional)** Directory path containing raw FastQ files. Required if `--sra-id` is not provided.
- `--sra-id <STR>`: **(Optional)** NCBI SRA Accession ID (e.g., `SRR123456`). Can be used multiple times to specify multiple IDs.
- `-o, --output <DIR>`: **(Required)** Analysis result output directory.
- `-d, --design <FILE>`: **(Required)** Experimental design CSV file path.
- `-s, --species <STR>`: **(Optional)** Species name (e.g., "Homo sapiens", "Mus musculus"). Used for automatic reference genome download and enrichment analysis.
- `--genome-fasta <FILE>`: **(Optional)** Local reference genome FASTA file path (overrides `--species`).
- `--genome-gtf <FILE>`: **(Optional)** Local genome annotation GTF file path (overrides `--species`).
- `-t, --threads <INT>`: **(Optional)** Number of parallel threads (default: 4).
- `--skip-qc`: Skip quality control step.
- `--skip-trim`: Skip trimming step (only do QC).
- `--star-align`: Enable STAR alignment and generate chromosome distribution plot.
- `--theme <STR>`: Specify plotting theme (default: `default`, optional: `nature`, `science`, etc.).

### 🔧 Advanced QC Options

These parameters will be passed directly to `fastp` for data cleaning:

- `--qualified-quality-phred <INT>`: Base quality threshold (Phred). Default 15 (Q15).
- `--unqualified-percent-limit <INT>`: Allowed percentage limit of low-quality bases (0-100). Default 40 (40%).
- `--n-base-limit <INT>`: Allowed N base count limit. Default 5.
- `--length-required <INT>`: Length filtering threshold, reads shorter than this will be discarded. Default 15.
- `--max-len1 <INT>`: Max length limit for Read1, excess part will be trimmed. Default 0 (unlimited).
- `--max-len2 <INT>`: Max length limit for Read2, excess part will be trimmed. Default 0 (unlimited).
- `--adapter-sequence <STR>`: Adapter sequence for Read1. Auto-detected if not provided.
- `--adapter-sequence-r2 <STR>`: Adapter sequence for Read2. Auto-detected if not provided.
- `--trim-front1 <INT>`: Trim bases from 5' end of Read1.
- `--trim-tail1 <INT>`: Trim bases from 3' end of Read1.
- `--cut-right`: Enable sliding window trimming from 3' end (cut_right).
- `--cut-window-size <INT>`: Window size for cut_right. Default 4.
- `--cut-mean-quality <INT>`: Mean quality threshold for cut_right. Default 20.
- `--dedup`: Enable deduplication.
- `--poly-g-min-len <INT>`: Minimum length detection threshold for polyG tail trimming. Default 10.

## 📦 Python API

### 1. Full Workflow (`RNASeqPipeline`)

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

# Returns merged counts matrix (DataFrame)
counts_df = manager.run()
```

### 4. Report Generation (`ReportGenerator`)

```python
from bio_analyze_rna_seq.report import ReportGenerator
from pathlib import Path

# Need to pass results from previous steps
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

This module depends on the following external tools, please ensure they are installed and available in the system PATH:

1. **fastp**: (Required) Used for data trimming and basic QC.
2. **salmon**: (Required) Used for quantification.
3. **fastqc**: (Optional) Used for generating detailed quality control reports. If not installed, only fastp will be used for QC.
4. **STAR**: (Optional) Used for alignment and chromosome distribution analysis if `--star-align` is enabled.
5. **samtools**: (Optional) Used for BAM file indexing and statistics if `--star-align` is enabled.
6. **gffread**: (Optional) Used to extract transcript sequences if genome FASTA+GTF are provided but no transcript FASTA.
7. **sra-tools**: (Optional) Must be installed (includes `prefetch` and `fasterq-dump`) if using `--sra-id` feature.
