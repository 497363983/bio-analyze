---
order: 1
---

# Introduction

Bio-analyze is a toolbox for common bioinformatics analysis tasks, organized as a monorepo with multiple independent modules, all accessible via a unified CLI and Python API.

## Module List

Currently, the toolkit includes the following core modules, each usable independently or via the CLI:

| Module Name                                       | Function Summary                                                                                 | Key Features                                     |
| :------------------------------------------------ | :----------------------------------------------------------------------------------------------- | :----------------------------------------------- |
| [**RNA-Seq Analysis**](../modules/bio-analyze-rna-seq/index.md)     | SRA download, QC (FastQC/fastp), Alignment (STAR), Quantification (Salmon), DE (DESeq2), Enrichment (GO/KEGG) | Fully automated pipeline, one-click HTML report, automatic reference genome handling |
| [**Plotting Tools**](../modules/bio-analyze-plot/index.md) | Volcano, Heatmap, PCA, Bar (w/ error bars/significance), Line, Pie, Chromosome Coverage          | Supports multiple chart types, highly customizable themes |
| [**Molecular Docking**](../modules/docking.md)    | Receptor/Ligand preparation, docking simulation configuration and execution                      | Simplified docking workflow, unified CLI interface |
| [**Core Components**](../modules/core.md)         | Logging, config loading, subprocess management, file IO                                          | Provides low-level common capabilities for all modules |
| [**CLI Entry**](../modules/cli.md)                | Unified CLI framework, plugin loading, template creation                                         | Provides `bioanalyze` main command, supports plugin extension |
