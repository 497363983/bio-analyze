# RNA-Seq Analysis Module Implementation Plan

## 1. Overview

Implement a comprehensive RNA-Seq analysis module (`bio-analyze-rna-seq`) that takes raw sequencing data and reference genome information to produce expression quantification, differential expression results, and a visual report.

## 2. Dependencies

* **Core**: `bio-analyze-core`

* **Plotting**: `bio-analyze-plot`

* **Analysis**:

  * `pydeseq2` (Differential Expression)

  * `gseapy` (Enrichment Analysis)

  * `pandas`, `numpy`, `scipy`

  * `scikit-learn` (for PCA)

* **Genome Management**: `genomepy` (Auto-download references)

* **Reporting**: `jinja2` (HTML templates)

* **External Tools (Wrappers)**:

  * `fastp` (QC & Trimming)

  * `salmon` (Quantification - Fast & Lightweight)

## 3. Module Structure

```
packages/rna_seq/
├── src/
│   └── bio_analyze_rna_seq/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point (typer)
│       ├── pipeline.py         # Main pipeline orchestrator
│       ├── genome.py           # Reference genome management (genomepy)
│       ├── qc.py               # fastp wrapper
│       ├── quant.py            # salmon wrapper
│       ├── de.py               # pydeseq2 analysis
│       ├── enrichment.py       # gseapy analysis
│       ├── report.py           # HTML report generation
│       └── utils.py            # Helper functions
├── templates/                  # Jinja2 templates for report
│   └── report.html
├── pyproject.toml
└── README.md
```

## 4. Implementation Steps

### Step 1: Configuration & Dependencies

* Update `packages/rna_seq/pyproject.toml` to include necessary Python dependencies.

* Ensure `bio-analyze-plot` is correctly linked.

### Step 2: CLI Interface (`cli.py`)

* Implement `run` command using `typer`.

* Arguments:

  * `input_dir`: Directory containing FastQ files.

  * `output_dir`: Directory for results.

  * `species`: Species name (e.g., "Homo sapiens") for auto-reference download.

  * `genome_fasta`: Path to genome FASTA (override species).

  * `genome_gtf`: Path to genome GTF (override species).

  * `design_file`: CSV file describing experimental design (samples & conditions).

  * `threads`: Number of threads for parallel processing.

### Step 3: Genome Management (`genome.py`)

* Implement `GenomeManager` class.

* Use `genomepy` to download/prepare reference if `species` is provided.

* validate provided FASTA/GTF paths.

### Step 4: Quality Control & Trimming (`qc.py`)

* Implement `FastpWrapper` class.

* Scan `input_dir` for FastQ files (paired or single end).

* Run `fastp` for each sample to generate cleaned reads and QC reports (`json`/`html`).

### Step 5: Quantification (`quant.py`)

* Implement `SalmonWrapper` class.

* Build Salmon index from reference transcriptome (if needed, extract from Genome+GTF or download).

* Run `salmon quant` for each sample.

* Merge quantification results into a count matrix.

### Step 6: Differential Expression (`de.py`)

* Use `pydeseq2` to perform DE analysis.

* Input: Count matrix + Design file.

* Output: DE results (log2FC, p-value, padj) for specified contrasts.

### Step 7: Visualization & Enrichment

* **PCA**: Implement PCA analysis using `scikit-learn` and plot using `matplotlib`/`seaborn` (or add to `bio-analyze-plot`).

* **Volcano/Heatmap**: Use `bio-analyze-plot` module.

* **Enrichment**: Use `gseapy` to perform GO/KEGG enrichment on DE genes.

### Step 8: Reporting (`report.py`)

* Create an HTML template summarizing:

  * Summary Stats (Reads, Mapping Rate).

  * QC Plots (Fastp summary).

  * PCA Plot.

  * Top DE Genes (Table).

  * Volcano & Heatmap Plots.

  * Enrichment Results.

* Use `jinja2` to render the report.

## 5. Verification

* Create a dummy dataset (small FastQ files) for testing.

* Run the full pipeline via CLI.

* Verify output files (counts, results.csv, report.html) exist and are correct.

