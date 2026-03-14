# bio-analyze-rna-seq

**bio-analyze-rna-seq** is the dedicated transcriptome analysis module in the `bio-analyze` toolkit. It provides an automated end-to-end solution from raw sequencing data to final visualization reports.

## ✨ Core Features

- **Automated Workflow**: One-click completion of all steps from FastQ to HTML report.
- **Flexible Configuration**: Supports command-line arguments as well as JSON/YAML configuration files.
- **Modular Execution**: Supports running specific steps of the analysis pipeline independently (e.g., only running QC or quantification).
- **SRA Auto Download**: Supports inputting NCBI SRA Accession IDs directly, automatically downloading and converting to FASTQ format.
- **Quality Control (QC)**: Generates professional QC reports using `FastQC` and integrates `fastp` for efficient data trimming and filtering.
- **Fast Quantification**: Uses `Salmon` for pseudo-alignment-based transcript quantification, which is extremely fast and accurate.
- **Differential Expression**: Based on native Python implementation of `PyDESeq2`, providing robust differential gene screening.
- **Enrichment Analysis**: Uses `GSEApy` for automated GO (Gene Ontology) and KEGG pathway enrichment analysis, as well as GSEA.
- **Visual Report**: Generates interactive HTML reports including PCA plots, volcano plots, heatmaps, enrichment results, and GSEA plots.
- **Auto Reference Genome**: Simply specify the species name (e.g., "Homo sapiens") to automatically download and build indices.

## 🚀 Quick Start (Usage)

### Scenario 1: Using Local Data

#### 1. Prepare Data

Put all FastQ files (`.fastq.gz` or `.fq.gz`) in a folder. Supports paired-end (`_R1`/`_R2` or `_1`/`_2`) and single-end sequencing data.

#### 2. Prepare Design File

Create a CSV file (e.g., `design.csv`) defining the relationship between samples and experimental conditions. Must contain `sample` and `condition` columns:

| sample  | condition |
| :------ | :-------- |
| sample1 | control   |
| sample2 | control   |
| sample3 | treated   |
| sample4 | treated   |

> **Note**: The names in the `sample` column must correspond to the FastQ filenames (excluding suffixes and `_R1`/`_R2` parts).

#### 3. Run Analysis

Start the analysis pipeline with the following command:

```bash
uv run bioanalyze rna_seq run \
    --input ./raw_data \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens" \
    --threads 8
```

### Scenario 2: Using SRA ID Directly

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

# Advanced QC config (optional)
qc:
  qualified_quality_phred: 20
  length_required: 30
  dedup: true
```

Then run:

```bash
uv run bioanalyze rna_seq run --config config.yaml
```

### Scenario 4: Step-by-Step

You can use independent subcommands to run specific steps in the analysis pipeline, offering greater flexibility.

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

#### 6. Differential Expression (de)
```bash
uv run bioanalyze rna_seq de --counts ./quant_results/counts.csv --design design.csv -o ./de_results
```

#### 7. Enrichment Analysis (enrich)
```bash
uv run bioanalyze rna_seq enrich --de-results ./de_results/deseq2_results.csv -s "Homo sapiens" -o ./enrich_results
```

## 📋 Command Details

### `run` (Full Pipeline)
Runs the complete RNA-Seq analysis pipeline.

### `download`
Downloads data from NCBI SRA and converts to FastQ format.
- `--sra-id`: SRA Accession ID.
- `-o, --output`: Output directory.

### `genome`
Prepares reference genome (download or index).
- `-s, --species`: Species name.
- `--fasta`: Local FASTA file.
- `--gtf`: Local GTF file.

### `qc`
Runs QC and trimming.
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
- `--counts`: Counts matrix CSV.
- `--design`: Design matrix CSV.

### `enrich`
Runs GO/KEGG enrichment analysis.
- `--de-results`: DESeq2 results CSV.
- `-s, --species`: Species name.

### `gsea`
Runs GSEA enrichment analysis.
- `--de-results`: DESeq2 results CSV.
- `-s, --species`: Species name.
- `--gene-sets`: Gene set library name (default: KEGG_2021_Human).
- `--ranking-metric`: Ranking metric (default: auto).

## 📋 `run` Command Parameters

- `-c, --config <FILE>`: **(Optional)** JSON/YAML config file path.
- `--step <STR>`: **(Optional)** Run specific step (`download`, `reference`, `qc`, `quant`, `de`, `enrichment`, `report`).
- `-i, --input <DIR>`: **(Optional)** Directory containing raw FastQ files. Required if `--sra-id` is not provided.
- `--sra-id <STR>`: **(Optional)** NCBI SRA Accession ID. Can be used multiple times.
- `-o, --output <DIR>`: **(Required)** Output directory.
- `-d, --design <FILE>`: **(Required)** Experimental design CSV file path.
- `-s, --species <STR>`: **(Optional)** Species name.
- `--genome-fasta <FILE>`: **(Optional)** Local reference genome FASTA path.
- `--genome-gtf <FILE>`: **(Optional)** Local genome annotation GTF path.
- `-t, --threads <INT>`: **(Optional)** Parallel threads (default: 4).
- `--skip-qc`: Skip QC step.
- `--skip-trim`: Skip trimming step (QC only).
- `--star-align`: Enable STAR alignment and generate chromosome distribution plot.
- `--theme <STR>`: Plotting theme (default: `default`).

### 🔧 Advanced QC Options

These parameters are passed directly to `fastp`:

- `--qualified-quality-phred <INT>`: Base quality threshold (Phred). Default 15 (Q15).
- `--unqualified-percent-limit <INT>`: Low quality base percentage limit (0-100). Default 40.
- `--n-base-limit <INT>`: N base count limit. Default 5.
- `--length-required <INT>`: Length filter threshold. Default 15.
- `--max-len1 <INT>`: Read1 max length. Default 0.
- `--max-len2 <INT>`: Read2 max length. Default 0.
- `--adapter-sequence <STR>`: Read1 adapter sequence.
- `--adapter-sequence-r2 <STR>`: Read2 adapter sequence.
- `--trim-front1 <INT>`: Read1 5' trim bases.
- `--trim-tail1 <INT>`: Read1 3' trim bases.
- `--cut-right`: Enable sliding window trimming from 3' end.
- `--cut-window-size <INT>`: Window size. Default 4.
- `--cut-mean-quality <INT>`: Mean quality threshold. Default 20.
- `--dedup`: Enable deduplication.
- `--poly-g-min-len <INT>`: polyG tail trimming min length. Default 10.

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

counts_df = manager.run()
```

### 4. Report Generation (`ReportGenerator`)

```python
from bio_analyze_rna_seq.report import ReportGenerator
from pathlib import Path

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

1. **fastp**: (Required) For data trimming and basic QC.
2. **salmon**: (Required) For quantification.
3. **fastqc**: (Optional) For detailed QC reports.
4. **STAR**: (Optional) For alignment.
5. **samtools**: (Optional) For BAM indexing/stats.
6. **gffread**: (Optional) For transcript extraction.
7. **sra-tools**: (Optional) For SRA download.
