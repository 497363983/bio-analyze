# Bio Analyze Development Guide

## Branch Strategy

> **IMPORTANT: Never develop on** **`main`** **branch!**
>
> - `main` = **production branch**. Only released or release-candidate code.
> - Create feature branch from `main`, merge back later.
>   - Name format: `<type>/<short-description>`
>     - `<type>`: `feat`, `fix`, `refactor`, `docs`, `test`
>     - `<short-description>`: short summary, use hyphens

## Architecture & Project Structure

- **Monorepo Architecture**: Python monorepo. Each tool module = independent distribution package.
- **Naming Conventions**:
  - **Distribution Packages**: Always use `bio-analyze-` prefix, like `bio-analyze-core`, `bio-analyze-plot`.
  - **Module Import Names**: Keep flat. Import direct, like `import bio_analyze_core`, `import rna_seq`. No unified top-level namespace.
- **Toolchain**:
  - **Dependency Management**: Use `uv`.
  - **Python Env Commands**: Run Python-dependent local commands with *`uv run`, like* *`uv run pytest`,* *`uv run python scripts/generate_metadata.py`,* *`uv run ruff check`. Do* not call bare `python`, `pytest`, `ruff` when project env matters.
  - **Code Formatting & Linting**: Use `ruff`, configured in root `pyproject.toml`.
  - **Testing Framework**: Use `pytest`.
- **Compatibility Requirements**:
  - **Python Versions**: Support Python **3.10 to 3.14**.
  - **Backward Compatibility**: New feature should keep backward compatibility as much as possible.
  - **Breaking Changes**: If unavoidable, document clearly. Release only in **major** version update, like v1.0.0 -> v2.0.0.
  - **Pre-release Versions**: Breaking change allowed between alpha/beta/rc, but keep compatibility with last stable release unless pre-release targets new major version.

## Module Directory Structure

New module under `packages/` must follow this structure:

```text
packages/<module_name>/
├── pyproject.toml         # Package metadata, uv dependencies, and entry points
├── README.md              # Documentation specific to this module
├── CHANGELOG.md           # Changelog (typically generated via git-cliff)
├── src/
│   └── bio_analyze_<module_name>/   # Main source code directory (using bio_analyze_ prefix)
│       ├── __init__.py
│       ├── cli.py         # CLI command definitions (BioAnalyzeTyper/Agentyper-compatible, if applicable)
│       └── commands/      # Subcommands implementations (if applicable)
├── tests/                 # Unit and integration tests (pytest)
│   ├── conftest.py        # Shared test fixtures
│   └── test_*.py          # Test files
└── metadata/              # (Optional) Generated CLI/API metadata for documentation
```

## Language & Comments

- **Code Comments**: English only.
- **Docstrings**: English only, except Chinese localization strings in i18n sections.
- **Log Messages**: English only.
- **CLI Help & Prompts**: Gettext-first i18n. Write new CLI help/prompt text as English `msgid`, then translate through module `locale/<lang>/LC_MESSAGES/messages.po` and `messages.mo`. Do not use `zh: ...\nen: ...` bilingual blocks in code comments, docstrings, or help strings.
- **Git Commit Messages**: English only.

## Documentation Standards

- **Synchronous Updates**: Any new feature, parameter change, or function change must update `doc/` at same time.
- **Unified Style**: Keep docs objective, professional, clear. Avoid conversational style.
- **Bilingual Support**: Update both English default docs and Chinese `zh/` docs when applicable.

## Coding Standards

- **Maintainability & Extensibility**: Design for maintainability and extensibility. Follow DRY. Extract common logic.
- **Core Extraction**: Generic utility used across modules goes to `bio_analyze_core`.
- **Module Independence**: Business modules must not depend on each other. Depend only on base modules like `core`, `plot`, `cli`.
- **CLI Architecture**: Plugin-based. Register to unified `BioAnalyzeTyper` CLI main program via Entry points. Core compatibility layer is built on Agentyper.
- **Unified Logging**:
  - CLI entry point does idempotent init with `bio_analyze_core.logging.setup_logging()`.
  - **Core Restriction**: Library code, like Pipeline constructors, must not call `setup_logging()` or reset global handlers. Library code only use `get_logger()` for context-bound logging.
- **Subprocess Execution**:
  - Never use native Python `subprocess.run` direct.
  - External binary commands must use core `bio_analyze_core.subprocess` methods `run` or `run_streaming`. This ensures built-in `timeout` and `tail_lines`.
- **Configuration Loader**:
  - If CLI command supports `--config`, reuse `bio_analyze_core.utils.load_config` for `.json`, `.yaml`/`.yml`, `.toml`.

## Testing Strategy

- **Test Coverage**: New code must keep at least **70%** coverage.
- **Test Data**: Store all test data/files in module `tests/data/`.
- **Plotting Regression Tests**: Plot tests must include visual regression checks.
- **Baseline Snapshots**: Store regression baselines in module `tests/snapshot/`.
- **Local Testing Environment**: Run local tests in **Docker**, especially on Windows, for consistency.
- **Mocking External Binary Dependencies**: For modules using external executables like `fastp`, `gnina`, mock `shutil.which` and `subprocess.run` heavily in unit tests. Avoid relying on local environment.
- **Parallel Workers in Tests**: With `pytest` `monkeypatch`, mocks do not propagate to child processes from `ProcessPoolExecutor`. Patch `ProcessPoolExecutor` to `ThreadPoolExecutor` during concurrent tests so mocks work.
- **Log Flushing for Short-lived Processes**: For short-lived child processes in Docker or Windows, watch `loguru` async writing. Call `logger.complete()` explicitly so log buffer flushes fully.

