# Development Environment Setup

If you want to contribute to the project or modify the code, follow these steps to set up your development environment.

## Using install scripts (install.sh / install.bat)

If you already have an environment or only want to install Python dependencies (including dev tools), use the install script:

**Linux / macOS / WSL:**

```bash
bash install.sh
```

**Windows (PowerShell / CMD):**

```cmd
install.bat
```

This script will:

1. Detect and install `uv` (if not installed).
2. Create `.venv` virtual environment (if not exists).
3. Install all modules and `pre-commit`, `commitizen`.
4. Automatically configure Git hooks.

## Manual Setup

If you prefer to set up manually:

```bash
# Create venv
uv venv

# Install dependencies in editable mode
uv pip install -e packages/core -e packages/cli -e packages/docking -e packages/plot -e packages/rna_seq

# Install dev tools
uv pip install pre-commit commitizen

# Install git hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## Code Quality

- **Automatic Check**: `pre-commit` runs formatting and linting on every commit.
- **Manual Check**: Run `pre-commit run --all-files`.
- **Commit Message**: Use `cz commit` to generate Conventional Commits compliant messages.
