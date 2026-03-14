# Installation

## One-Click Script (Linux/macOS/WSL)

If you are unfamiliar with Docker or want to run the toolkit directly in your local environment, we provide an automated installation script. This script automatically creates a Conda environment and installs all necessary dependencies.

### Prerequisites

- **OS**: Linux (Ubuntu recommended), macOS, or Windows WSL (Windows Subsystem for Linux).
- **Conda**: [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Mambaforge](https://github.com/conda-forge/miniforge) must be installed.

### Run Installation Script

Run in the project root:

```bash
bash setup.sh
```

The script will automatically:

1. Check Conda/Mamba environment.
2. Configure software sources like Bioconda.
3. Create a virtual environment named `bio_analyse_env`.
4. Install bioinformatics tools like `fastp`, `salmon`, `star`, `samtools`.
5. Install all `bio-analyse` modules.
6. Install and configure `pre-commit` and `commitizen`.

### Activate Environment

After installation, follow the prompts to activate the environment:

```bash
conda activate bio_analyse_env
bioanalyze --help
```

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

### Enter Interactive Shell

```bash
docker run -it --rm --entrypoint bash -v $(pwd)/data:/data bio-analyze:latest
```
