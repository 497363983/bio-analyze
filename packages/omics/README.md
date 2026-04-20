# bio-analyze-omics

[![codecov](https://codecov.io/gh/497363983/bio-analyze/graph/badge.svg?token=I78TXQBORK&component=omics)](https://codecov.io/gh/497363983/bio-analyze)

**bio-analyze-omics** is the omics analysis module in the `bio-analyze` toolbox. It currently includes the `rna_seq` transcriptomics submodule and exposes it through the unified `omics` CLI plugin.

## Included Submodules

- `rna_seq`: Transcriptomics workflow covering SRA download, QC, alignment, quantification, differential expression, enrichment, and report generation.

## Quick Start

```bash
uv run bioanalyze omics rna_seq run \
    --input ./raw_data \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens" \
    --threads 8
```

For species that are hard to resolve by name in `genomepy`, prefer an assembly accession:

```bash
uv run bioanalyze omics rna_seq run \
    --input ./raw_data \
    --output ./analysis_results \
    --design ./design.csv \
    --assembly GCA_013347765.1 \
    --threads 8
```

If you provide `--species`, the CLI now searches candidate genomes with `genomepy.search()`, shows the matches, and lets you pick one before downloading.

## Python API

```python
from pathlib import Path

from bio_analyze_omics.rna_seq.pipeline import RNASeqPipeline

pipeline = RNASeqPipeline(
    input_dir=Path("./raw_data"),
    output_dir=Path("./results"),
    design_file=Path("design.csv"),
    species="Homo sapiens",
    threads=8,
    skip_qc=False,
)

pipeline.run()
```
