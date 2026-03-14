# Introduction

Bio-analyze is a toolkit for common bioinformatics analysis tasks, organized as a monorepo with multiple independent modules, callable via a unified CLI and Python API.

## Modules List

Currently, the toolkit includes the following core modules, each usable independently or via the CLI:

| Module Name                 | Path                 | Function                                                                                                      | Key Features                                                           |
| :-------------------------- | :------------------- | :------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------- |
| **RNA-Seq Analysis**  | `packages/rna_seq` | SRA Download, QC (FastQC/fastp), Alignment (STAR), Quantification (Salmon), DE (DESeq2), Enrichment (GO/KEGG) | Fully automated pipeline, one-click HTML report, auto reference genome |
| **Plotting Tools**    | `packages/plot`    | Volcano, Heatmap, PCA, Bar (with error bars/significance), Line, Pie, Chromosome                              | Supports diverse chart types, fully customizable themes                  |
| **Molecular Docking** | `packages/docking` | Receptor/Ligand preparation, docking simulation configuration & execution                                     | Simplified docking workflow, unified CLI interface                     |
| **Core Components**   | `packages/core`    | Logging, config loading, subprocess management, file IO                                                       | Underlying common capabilities for all modules                         |
| **CLI Entry**         | `packages/cli`     | Unified CLI framework, plugin loading, template creation                                                      | Provides `bioanalyze` main command, supports plugin extension        |
