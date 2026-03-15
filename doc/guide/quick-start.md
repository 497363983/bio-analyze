---
order: 3
---

# Quick Start

This guide will help you get started with `bio-analyze` quickly for common bioinformatics tasks.

## 1. Verify Installation

First, ensure `bio-analyze` is correctly installed:

```bash
bio-analyze --version
```

## 2. Basic Usage

### Plotting a Volcano Plot

The most common task is visualizing differential expression results.

1. **Prepare Data**: A CSV file with `log2FoldChange` and `padj` (or p-value) columns.
2. **Run Command**:

```bash
bio-analyze plot volcano results.csv --fc-cutoff 1.5 --p-cutoff 0.05
```

This will generate a `volcano.png` (or PDF) in the current directory.

### Running an RNA-Seq Workflow

To run a complete RNA-Seq analysis pipeline (from raw reads to expression matrix):

```bash
# Initialize a new project configuration
bio-analyze rna-seq init my_project

# Edit the config.yaml to specify your FASTQ files and reference genome

# Run the pipeline
bio-analyze rna-seq run --config my_project/config.yaml
```

## 3. Getting Help

You can always use the `--help` flag to see available commands and options for any module:

```bash
# List all modules
bio-analyze --help

# Get help for a specific module (e.g., plot)
bio-analyze plot --help

# Get help for a specific plot type
bio-analyze plot volcano --help
```

## Next Steps

- Explore the **Modules** section to learn about specific tools (Plotting, RNA-Seq, etc.).
- Check the **Examples** for more complex use cases.
