---
---

# quant

Quantify transcript or gene expression with an extensible plugin-based framework.

The quantification subsystem supports multiple backends with a unified result model.
Current backends include:

- `salmon`
- `kallisto`
- `featurecounts`
- `htseq-count`
- `rsem`

The framework standardizes:

- Tool selection and dependency checks
- Reference preparation and transcript FASTA extraction
- Parameter templates and per-tool custom phases
- Standard output files (`counts.csv`, metric matrices, result manifest)
- Cross-tool comparison output for reuse and validation

## CLI Usage

**Command**: `quant`

### Arguments

<ParamTable params-path="omics/rna_seq_quant_cli" />

### Example

```bash
uv run bioanalyze omics rna_seq quant \
  -i ./clean_data \
  -o ./quant_results \
  --fasta genome.fa \
  --gtf genes.gtf \
  --tool salmon \
  --compare-tool kallisto
```

## Architecture

### Core Components

- `QuantManager`: orchestration layer that selects the primary quantifier, optionally runs comparison backends, and writes standardized outputs
- `BaseQuantifier`: quant-specific engine contract built on top of `bio_analyze_core.engine.BaseEngine`
- `QuantifierRegistry`: compatibility registry facade backed by `bio_analyze_core.engine.EngineRegistry`
- `QuantRunResult`: unified result object with counts matrix, metric matrices, sample outputs, metadata, and manifests

### Shared Engine Integration

- Quantification engines now register under the shared `bio_analyze.engine` entry-point group
- Domain name: `quant`
- Engine names currently include `salmon`, `kallisto`, `featurecounts`, `htseq-count`, and `rsem`
- `QuantManager` internally delegates engine creation and switching to `bio_analyze_core.engine.EngineManager`

### Standard Output Layout

- `counts.csv`: normalized primary count matrix used by downstream DE modules
- `result_manifest.json`: metadata, sample outputs, and tool summary
- `tpm.csv`, `length.csv`, or backend-specific metric matrices when available
- `comparisons/<tool>/...`: standardized outputs for comparison backends
- `tool_comparison.csv`: cross-tool Pearson correlation table when comparison tools are enabled

### Backend Modes

- Read-based: `salmon`, `kallisto`, `rsem`
- Alignment-based: `featurecounts`, `htseq-count`

The manager automatically reuses sibling `align/` BAM files for alignment-based tools when available.

## Python API

### Primary Quantification

```python
from pathlib import Path

from bio_analyze_omics.rna_seq.quant import QuantManager

reads = {
    "sample1": {"R1": Path("sample1_1.fq.gz"), "R2": Path("sample1_2.fq.gz")},
    "sample2": {"R1": Path("sample2_1.fq.gz"), "R2": Path("sample2_2.fq.gz")},
}
reference = {
    "fasta": Path("genome.fa"),
    "gtf": Path("genes.gtf"),
}

manager = QuantManager(
    reads=reads,
    reference=reference,
    output_dir=Path("./quant_results"),
    threads=8,
    tool="salmon",
    compare_tools=["kallisto"],
    tool_config={
        "template": "default",
        "sample_workers": 2,
        "phases": {"quant": ["--seqBias", "--gcBias"]},
    },
)

counts_df = manager.run()
comparison_df = manager.get_comparison_table()
```

### Tool Discovery

```python
from bio_analyze_omics.rna_seq.quant import list_available_quantifiers

print(list_available_quantifiers())
```

## Configuration Model

The `run` command accepts a `quant` section from the loaded config file:

```yaml
quant:
  tool: salmon
  compare_tools:
    - kallisto
  primary:
    template: default
    sample_workers: 2
    phases:
      quant:
        - --seqBias
        - --gcBias
  compare:
    kallisto:
      template: bootstrap
      phases:
        quant:
          - -b
          - "50"
```

### Template Semantics

- `template`: selects a backend-specific preset
- `phases.index`: extra arguments appended to index / reference build commands
- `phases.quant`: extra arguments appended to quantification commands
- `sample_workers`: optional per-sample parallelism for sample-oriented backends
- `params`: structured backend options such as `library_type`, `fragment_length`, or `fragment_sd`

## Extension Guide

To add a new quantification backend:

1. Subclass `BaseQuantifier`
2. Define `TOOL_NAME`, `MODE`, and `REQUIRED_BINARIES`
3. Implement `execute()` and optional helper methods such as `build_index()` or `quantify_sample()`
4. Return a `QuantRunResult`
5. Register the backend with `@register_quantifier`
6. Add focused unit tests for command construction, parsing, and normalized outputs

Minimal example:

```python
from bio_analyze_omics.rna_seq.quant import (
    BaseQuantifier,
    QuantRunResult,
    register_quantifier,
)


@register_quantifier
class MyQuantifier(BaseQuantifier):
    TOOL_NAME = "mytool"
    MODE = "reads"
    REQUIRED_BINARIES = ("mytool",)

    def execute(self) -> QuantRunResult:
        # build commands, run tool, parse outputs
        counts = ...
        return QuantRunResult(
            tool=self.TOOL_NAME,
            output_dir=self.output_dir,
            counts_matrix=counts,
        )
```

## Testing Strategy

- Unit tests:
  - Verify command construction, dependency checks, template expansion, and output parsing for each quantifier
  - Mock external binaries instead of invoking local installations directly
  - Validate standardized files such as `counts.csv`, metric matrices, and `result_manifest.json`
- Integration tests:
  - Run `QuantManager` with a primary backend and at least one comparison backend
  - Verify alignment-backed tools can reuse `align/` BAM outputs when present
  - Confirm cross-tool comparison output is written to `tool_comparison.csv`
- Regression focus:
  - Protect resume scenarios, incomplete index rebuilds, compressed annotation handling, and configuration loading
  - Add backend-specific tests only when they reduce interoperability risk or parsing ambiguity

## Notes

- Salmon and Kallisto quantify transcript-level targets and can optionally emit abundance-oriented matrices.
- FeatureCounts and HTSeq-count consume alignment BAM files and gene annotations.
- For mapping-based Salmon workflows, a decoy-aware transcriptome is recommended for best accuracy.
