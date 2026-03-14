# bio-analyze-cli

**bio-analyze-cli** is the unified command-line entry point for the BioAnalyze toolkit. It is responsible for dynamically discovering and loading various functional modules (such as `rna-seq`, `docking`, `plot`, etc.) and providing a unified CLI experience.

## 🚀 Core Features

- **Plugin Architecture**: Automatically discovers installed `bio-analyze-*` modules (e.g., `bio-analyze-docking`, `bio-analyze-plot`) based on `entry points`.
- **Unified Configuration**: Supports global configuration file loading and log management.

## 🛠️ Common Commands

### 1. Basic Commands

```bash
# View help
bioanalyze --help

# View installed plugins
bioanalyze plugins
```

### 2. Calling Submodules

Once the corresponding function module package is installed, it can be called directly via `bioanalyze`:

```bash
# Run RNA-Seq pipeline
bioanalyze rna_seq run --input ./data --output ./results

# Run Molecular Docking
bioanalyze docking run --receptor rec.pdb --ligand lig.sdf

# Run Plotting Tool
bioanalyze plot volcano results.csv
```
