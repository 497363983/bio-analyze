# Bio Analyze Development Guide

## Branch Strategy

> **IMPORTANT: Never develop on `main` branch!**
>
> - `main` is the **production branch** — it only contains released or release candidate versions
> - Feature branches should be created from `main` and merged back
>   - Name format: `<type>/<short-description>`
>     - `<type>`: One of `feat`, `fix`, `refactor`, `docs`, `test`
>     - `<short-description>`: A brief description of the work (use hyphens for spacing)

## Architecture & Project Structure

- **Monorepo Architecture**: The project uses a Python monorepo structure. Each tool module is maintained as an independent distribution package.
- **Naming Conventions**:
  - **Distribution Packages**: Always use the `bio-analyse-` prefix (e.g., `bio-analyse-core`, `bio-analyse-plot`).
  - **Module Import Names**: Keep it flat. Import modules directly by their names (e.g., `import bio_analyze_core`, `import rna_seq`) without a unified top-level namespace.
- **Toolchain**:
  - **Dependency Management**: Use `uv`.
  - **Code Formatting & Linting**: Use `ruff` (configured globally in `pyproject.toml` at the root directory).
  - **Testing Framework**: Use `pytest`.
- **Compatibility Requirements**:
  - **Python Versions**: The project strictly supports Python versions from **3.9 to 3.14**. All code must be compatible within this range.
  - **Backward Compatibility**: New features should prioritize backward compatibility to the greatest extent possible.
  - **Breaking Changes**: If a breaking change is unavoidable, it must be clearly documented and only released in a **major** version update (e.g., v1.0.0 -> v2.0.0).
  - **Pre-release Versions**: Breaking changes are permitted between pre-release versions (alpha, beta, rc), provided they maintain compatibility with the last stable release (unless the pre-release is explicitly for a new major version).

## Module Directory Structure

To ensure consistency across the monorepo, any new module added to the `packages/` directory must strictly follow this standard directory structure:

```text
packages/<module_name>/
├── pyproject.toml         # Package metadata, uv dependencies, and entry points
├── README.md              # Documentation specific to this module
├── CHANGELOG.md           # Changelog (typically generated via git-cliff)
├── src/
│   └── bio_analyze_<module_name>/   # Main source code directory (using bio_analyze_ prefix)
│       ├── __init__.py
│       ├── cli.py         # Typer CLI commands definitions (if applicable)
│       └── commands/      # Subcommands implementations (if applicable)
├── tests/                 # Unit and integration tests (pytest)
│   ├── conftest.py        # Shared test fixtures
│   └── test_*.py          # Test files
└── metadata/              # (Optional) Generated CLI/API metadata for documentation
```

## Language & Comments

- **Code Comments**: Must be written in **English**.
- **Docstrings**: Must be written in **English**, EXCEPT for the Chinese localization strings in i18n sections.
- **Log Messages**: Must be written in **English**.
- **CLI Help & Prompts**: Supports bilingual i18n. Use the fixed format when writing docstrings for CLI commands: `zh: [Chinese Content]\nen: [English Content]`.
- **Git Commit Messages**: Must be written in **English**.

## Documentation Standards

- **Synchronous Updates**: Whenever there is a new feature, a parameter change, or any functional modification, the documentation in the `doc/` directory MUST be updated synchronously.
- **Unified Style**: All documentation must adhere to a consistent style. Keep descriptions objective, professional, and clear. Avoid overly conversational or colloquial language.
- **Bilingual Support**: Since the project supports bilingual CLI and documentation, ensure that updates are reflected in both the English (default) and Chinese (`zh/`) documentation directories where applicable.

## Coding Standards

- **Maintainability & Extensibility**: Always design with maintainability and extensibility in mind. Follow the DRY (Don't Repeat Yourself) principle by extracting common logic to avoid repetitive code.
- **Core Extraction**: If a method or utility is generic enough to be used across multiple modules, extract it and move it to the `bio_analyze_core` module for global sharing.
- **Module Independence**: Business modules MUST NOT depend on each other to prevent tight coupling. They should only depend on foundational modules such as `core`, `plot`, and `cli`.
- **CLI Architecture**: Modules use a plugin-based design and are registered to the unified Typer CLI main program via Entry points.
- **Unified Logging**:
  - Idempotent initialization is performed by calling `bio_analyze_core.logging.setup_logging()` at the CLI entry point.
  - **Core Restriction**: Library code (e.g., various Pipeline constructors) is **STRICTLY PROHIBITED** from calling `setup_logging()` or resetting global handlers. Library code can only use `get_logger()` to bind context and output logs.
- **Subprocess Execution**:
  - Never use the native Python `subprocess.run` directly.
  - When executing external binary commands, always use the `run` or `run_streaming` methods provided by the core module `bio_analyze_core.subprocess`. This ensures the built-in `timeout` and `tail_lines` (tail error log capturing) mechanisms are utilized.
- **Configuration Loader**:
  - If a CLI command supports the `--config` option, reuse the `bio_analyze_core.utils.load_config` function to support `.json`, `.yaml`/`.yml`, and `.toml` formats by default.

## Testing Strategy

- **Test Coverage**: New code must maintain a test coverage of **at least 70%**.
- **Test Data**: All test data and files must be uniformly stored in the `tests/data/` directory of the corresponding module.
- **Plotting Regression Tests**: Tests for plotting functions must include visual regression testing to verify the generated images.
- **Baseline Snapshots**: Baseline files for regression testing must be uniformly stored in the `tests/snapshot/` directory of the corresponding module.
- **Local Testing Environment**: When running tests locally, especially on Windows systems, you must use a **Docker environment** to ensure consistency and avoid environment-specific issues.
- **Mocking External Binary Dependencies**: For modules involving external executables (e.g., `fastp`, `gnina` in `rna_seq` or `docking`), you must extensively mock `shutil.which` and `subprocess.run` in unit tests to avoid over-reliance on the local environment.
- **Parallel Workers in Tests**: When using `pytest`'s `monkeypatch`, mocks cannot be propagated to child processes created by `ProcessPoolExecutor`. When testing concurrent code, temporarily patch `ProcessPoolExecutor` with `ThreadPoolExecutor` to ensure mocks take effect.
- **Log Flushing for Short-lived Processes**: When testing short-lived child processes in Docker or Windows environments, pay attention to `loguru`'s asynchronous writing features. You must explicitly call `logger.complete()` to ensure the log buffer is fully flushed, preventing data loss.
