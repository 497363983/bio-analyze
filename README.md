# bio-analyze

[![CI](https://github.com/497363983/bio-analyze/actions/workflows/ci.yml/badge.svg)](https://github.com/497363983/bio-analyze/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/497363983/bio-analyze/graph/badge.svg?token=I78TXQBORK)](https://codecov.io/gh/497363983/bio-analyze)

A toolbox for common bioinformatics analysis tasks, organized as a monorepo with multiple independent modules, accessible through a unified CLI and Python API.

## Monorepo Structure

- `packages/core`: Common utilities (configuration, logging, I/O, external command execution, resource management)
- `packages/cli`: Unified command-line entry point with plugin support for loading module subcommands
- `packages/*`: Various analysis tool modules (e.g., rna-seq, docking), each as an independently publishable package

## 📦 Available Modules

The toolbox currently includes the following core modules, each can be used independently or through the CLI:

| Module Name              | Path                 | Description                                                                                      | Key Features                                      |
| :----------------------- | :------------------- | :----------------------------------------------------------------------------------------------- | :----------------------------------------------- |
| 🧬**RNA-Seq Analysis** | `packages/rna_seq` | SRA download, QC (FastQC/fastp), alignment (STAR), quantification (Salmon), differential expression (DESeq2), enrichment analysis (GO/KEGG) | Fully automated pipeline, one-click HTML report generation, automatic reference genome |
| 📊**Plotting Tools**     | `packages/plot`    | Volcano plots, heatmaps, PCA, bar charts (with error bars/significance markers), line plots, pie charts, chromosome coverage plots, MSA plots, phylogenetic trees | Nature/Science themes, Chinese support, publication quality |
| 🧪**Molecular Docking** | `packages/docking` | Receptor/ligand preparation, docking simulation configuration and execution                     | Simplified docking workflow, unified CLI interface |
| 🧬**MSA & Phylogeny** | `packages/msa`     | Multiple Sequence Alignment (MAFFT, MUSCLE, Python), Phylogenetic tree construction (Distance-based, FastTree) | Seamless integration with external tools, pure Python fallback, automated tree building |
| 🛠️**Core Components** | `packages/core`    | Log management, configuration loading, subprocess management, file I/O                          | Provides underlying common capabilities for all modules |
| 🖥️**CLI Entry Point** | `packages/cli`     | Unified CLI framework, plugin loading, template creation                                         | Provides `bioanalyze` main command with plugin extension support |

## Design Principles

- **Independent module publishing, on-demand installation**: Each tool module is an independent distributable package, registering CLI subcommands via entry points
- **Common logic extraction**: Cross-module reusable functionality is unified in `core`
- **CLI and Python API parallel**: Same capabilities can be called via command line or imported as a library

## Quick Start (Development Mode)

```powershell
uv venv
uv pip install -e packages/core -e packages/cli -e packages/transcriptome -e packages/docking -e packages/msa -e packages/plot
.venv\Scripts\bioanalyze.exe plugins
```

## Development Environment Setup

To ensure code quality and commit standards, this project is configured with `pre-commit` and `commitizen`.

### 1. Install Development Tools

Make sure `pre-commit` is installed in your virtual environment:

```bash
uv pip install pre-commit commitizen
```

### 2. Enable Git Hooks

Run in the project root directory:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

### 3. Code Checking and Committing

- **Automatic checks**: Code formatting and checking runs automatically on each `git commit`
- **Manual checks**: Run `pre-commit run --all-files` to check all files
- **Standardized commits**: Use `cz commit` to generate commit messages following Conventional Commits specification

## One-Click Installation Script (Linux/macOS/WSL)

If you're not familiar with Docker or want to run the toolbox directly in your local environment, we provide an automated installation script. This script will automatically create a Conda environment and install all necessary dependencies.

### Prerequisites

- **Operating System**: Linux (Ubuntu recommended), macOS, or Windows WSL (Windows Subsystem for Linux)
- **Conda**: Must have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Mambaforge](https://github.com/conda-forge/miniforge) installed

### Run Installation Script

Run in the project root directory:

```bash
bash setup.sh
```

The script will automatically execute the following steps:

1. Check Conda/Mamba environment
2. Configure software sources including Bioconda
3. Create a virtual environment named `bio_analyse_env`
4. Install bioinformatics tools like `fastp`, `salmon`, `star`, `samtools`
5. Install all modules of the `bio-analyze` toolbox
6. Install and configure `pre-commit` and `commitizen`

### Activate Environment

After installation completes, activate the environment as prompted:

```bash
conda activate bio_analyse_env
bioanalyze --help
```

### Development Environment Installation (install.sh / install.bat)

If you already have an environment or only want to install Python dependencies (including development tools), use the installation script:

**Linux / macOS / WSL:**

```bash
bash install.sh
```

**Windows (PowerShell / CMD):**

```cmd
install.bat
```

This script will:

1. Detect and install `uv` (if not installed)
2. Create `.venv` virtual environment (if it doesn't exist)
3. Install all modules plus `pre-commit` and `commitizen`
4. Automatically configure Git hooks

## Using Docker (Recommended)

To simplify environment configuration, especially for complex bioinformatics tool dependencies, we provide Docker support.

### Build Image

```bash
docker build -t bio-analyze:latest .
```

### Run Container

```bash
# Mount data directory and run
docker run -it --rm -v $(pwd)/data:/data bio-analyze:latest --help
```

Or use `docker-compose`:

```bash
docker-compose run --rm bio-analyze --help
```

### Interactive Shell Access

```bash
docker run -it --rm --entrypoint bash -v $(pwd)/data:/data bio-analyze:latest
```

### Docker Environment Testing Guide

For Windows users or developers who don't want to install complex dependencies locally, we provide a convenient way to run tests in Docker containers. The environment automatically mounts local code, data directory (`data`), and output directory (`output`), so:

1. Code modifications can be tested without rebuilding the image
2. Test code can directly access files in the `data` directory
3. Test-generated reports or files can be directly viewed in the local `output` directory

**Windows (PowerShell):**

```powershell
.\run_tests_docker.ps1
```

**Linux / macOS:**

```bash
./run_tests_docker.sh
```

This will automatically build the test image and run all test cases.

## Adding a New Tool Module (Conventions)

1. Create an independent package under `packages/<module>/` (`pyproject.toml` + `src/`)
2. Depend on the common module: `bio-analyze-core`
3. Register CLI plugin entry point:

```toml
[project.entry-points."bio_analyze.cli"]
<module> = "bio_analyze.<module>.cli:get_app"
```

4. Implement `get_app()` in `bio_analyze.<module>.cli` and return a `typer.Typer` instance

## License

This project is licensed under the [GPL-3.0](LICENSE) open source license.
