# Development Environment Setup

If you want to contribute to the project or modify the code, please follow these steps to set up your development environment.

## Using Install Scripts (install.sh / install.bat)

If you already have an environment or only want to install Python dependencies (including development tools), you can use the install script:

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
2. Create a `.venv` virtual environment (if it doesn't exist).
3. Install all modules and `pre-commit`, `commitizen`.
4. Automatically configure Git hooks.

## Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
uv venv

# Install dependencies in editable mode
uv pip install -e packages/core -e packages/cli -e packages/docking -e packages/plot -e packages/rna_seq

# Install development tools
uv pip install pre-commit commitizen

# Install git hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## Code Quality

- **Automatic Check**: Code formatting and checking are automatically run on every `git commit`.
- **Manual Check**: Run `pre-commit run --all-files` to check all files.
- **Standardized Commit**: It is recommended to use `cz commit` to generate commit messages that comply with Conventional Commits specifications.
