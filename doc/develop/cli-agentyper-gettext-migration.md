# CLI Agentyper And Gettext Migration

## Summary

- Migrate the shared CLI compatibility layer in `bio_analyze_core.cli.app` from Typer-first behavior to an Agentyper-first compatibility facade.
- Introduce gettext-based runtime translation in core through `get_translator()` and translator-aware CLI localization.
- Move metadata generation to a JSON-Schema-first flow before converting to the existing metadata shape.
- Limit the RNA-Seq migration scope to `packages/omics`; `packages/rna_seq` remains outside this migration.

## Dependency Changes

- Added `agentyper>=0.1.12` for Python `>=3.10`.
- Added `polib>=1.2.0` for catalog loading, `.po` development reload, and `.mo` compilation.
- Removed Python 3.9 support and dropped the temporary Typer fallback.

## Interface Mapping

| Previous | Current |
| --- | --- |
| `typer.Typer` | `bio_analyze_core.cli.app.BioAnalyzeTyper` |
| `typer.Option` | `bio_analyze_core.cli.app.Option` |
| `typer.Argument` | `bio_analyze_core.cli.app.Argument` |
| `typer.Context` | `bio_analyze_core.cli.app.Context` |
| `typer.Exit` | `bio_analyze_core.cli.app.Exit` |
| `typer.testing.CliRunner` | `bio_analyze_core.cli.app.CliRunner` |
| `zh:/en:` runtime filtering | gettext translator with English `msgid` |

## Gettext Design

- `bio_analyze_core.i18n_gettext.get_translator(localePath)` returns a cached translator instance per locale directory.
- Language resolution order is:
  1. explicit runtime language
  2. config `bio_analyze.language`
  3. environment `LC_ALL` / `LC_MESSAGES` / `LANG`
  4. fallback `en_US`
- Production mode prefers `.mo`.
- Development mode can reload from `.po` using `polib`.
- Missing catalogs fall back to `en_US`, then identity translation.

## Metadata Pipeline

- CLI command metadata now flows through:
  1. `bio_analyze_core.metadata.schema.build_cli_schema()`
  2. `bio_analyze_core.metadata.convert.schema_to_metadata()`
- Generated metadata still preserves the existing `{"zh": "...", "en": "..."}` description layout for downstream consumers.

## Current Known Differences

- Agentyper exposes verbose mode primarily as `-v`; the compatibility layer accepts that behavior and keeps command behavior aligned even when `--verbose` is not rendered in help.
- CLI help body text may still prefer callback docstrings in some Agentyper code paths; option help translation is already applied through translator-aware parameter mutation.
- Python 3.9 support is intentionally dropped; the CLI stack now targets Python 3.10-3.14 only.
- `packages/omics` currently contains unrelated pre-existing syntax issues in user-modified files, which block full root CLI test execution until those files are fixed.

## Delivered Files

- Core CLI facade: `packages/core/src/bio_analyze_core/cli/app.py`
- Core gettext translator: `packages/core/src/bio_analyze_core/i18n_gettext.py`
- Translator bridge: `packages/core/src/bio_analyze_core/i18n.py`
- CLI localization: `packages/core/src/bio_analyze_core/cli_i18n.py`
- Metadata schema layer: `packages/core/src/bio_analyze_core/metadata/`
- Locale tooling: `scripts/extract_messages.py`, `scripts/compile_messages.py`

## Validation Snapshot

- Passed:
  - `packages/core/tests/test_cli_app.py`
  - `packages/core/tests/test_gettext_translator.py`
  - `packages/core/tests/test_cli_i18n.py`
- Blocked:
  - Root CLI regression tests are currently blocked by a pre-existing syntax error in `packages/omics/src/bio_analyze_omics/rna_seq/align/__init__.py`.
