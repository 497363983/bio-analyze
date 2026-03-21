# bio-analyze-cli

**bio-analyze-cli** is the unified command-line entry point for the BioAnalyze toolbox. It is responsible for dynamically discovering and loading various functional modules (such as `rna-seq`, `docking`, `plot`, etc.) and providing a unified CLI experience.

## 🚀 Core Features

- **Plugin Architecture**: Based on the `entry points` mechanism, it automatically discovers installed `bio-analyze-*` modules (e.g., `bio-analyze-docking`, `bio-analyze-plot`).
- **Unified Configuration**: Supports global configuration file loading and log management.
- **Scaffolding Tool**: Built-in `create` command to quickly generate templates for new tools or plotting themes.

## 🛠️ Common Commands

### 1. Basic Commands

```bash
# View help
bioanalyze --help

# View installed plugins
bioanalyze plugins
```

### 2. Invoking Submodules

Once the corresponding functional module package is installed, it can be directly invoked via `bioanalyze`:

```bash
# Run RNA-Seq pipeline
bioanalyze rna_seq run --input ./data --output ./results

# Run molecular docking
bioanalyze docking run --receptor rec.pdb --ligand lig.sdf

# Run plotting tools
bioanalyze plot volcano results.csv
```

### 3. Creating New Projects/Templates

Use the `create` command to quickly generate a standard project structure.

**Interactive Creation:**

```bash
bioanalyze create
```

(Then follow the prompts to select the type and enter the name)

**Quickly Create a New Tool:**

```bash
bioanalyze create tool --name my-new-tool
```

This will generate a new analysis module template under `packages/my-new-tool`.

**Quickly Create a Plotting Theme:**

```bash
bioanalyze create theme --name my-company-theme
```

This will generate a Python package named `my-company-theme` in the current directory. You can modify its `__init__.py` to customize the styles for `bio-plot`.

## 🔧 Development Guide

### Adding a New Module

1. Use `bioanalyze create tool` to create a template.
2. Configure `[project.entry-points."bio_analyze.plugins"]` in `pyproject.toml`.
3. Implement the `get_app()` function to return a `typer.Typer` instance.
4. Run `uv sync` to install the new module.
5. You can now invoke your new tool via `bioanalyze <tool-name>`.
