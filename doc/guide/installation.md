---
order: 2
---
# Installation

`bio-analyze` is a powerful bioinformatics analysis toolkit that supports installation via Conda, Pip, or Docker.

## Method 1: Install via Conda (Recommended)

Conda is the preferred installation method as it automatically handles complex bioinformatics software dependencies (such as `samtools`, `star`, etc.).

### 1. Install Conda/Mamba

First, ensure you have installed [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Mambaforge](https://github.com/conda-forge/miniforge) (recommended for faster speed).

### 2. Create Environment and Install

```bash
# Create a new environment named bio-analyze
conda create -n bio-analyze -c bioconda -c conda-forge bio-analyze

# Activate environment
conda activate bio-analyze
```

### 3. Verify Installation

```bash
bio-analyze --version
```

## Method 2: Install via Pip

If you only need Python-based analysis modules (like plotting, statistical analysis) and have already configured the bioinformatics tools environment, you can install via pip.

```bash
pip install bio-analyze
```

> **Note**: This method will NOT install external binary dependencies like `star` or `salmon`. You need to ensure these tools are in your system PATH manually.

## Method 3: Use Docker Image

If you don't want to configure the local environment, you can directly use our pre-built Docker image which contains all necessary tools.

### Pull Image

```bash
docker pull bioanalyze/bio-analyze:latest
```

### Run Analysis

Mount your local data directory to the container (e.g., current directory `$(pwd)` mounted to `/data`):

```bash
docker run --rm -v $(pwd):/data bioanalyze/bio-analyze:latest \
    bio-analyze plot volcano /data/results.csv
```

## Troubleshooting

### Dependency Conflicts

If you encounter dependency conflicts, try creating a clean environment or use `mamba` instead of `conda` for faster and better dependency resolution:

```bash
mamba create -n bio-analyze -c bioconda -c conda-forge bio-analyze
```
