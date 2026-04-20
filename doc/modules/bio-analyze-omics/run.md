---
---

# run

Run the complete RNA-Seq pipeline.

## CLI Usage

**Command**: `run`

### Arguments

<ParamTable params-path="omics/rna_seq_run_cli" />

### Advanced QC Options

- `--fastqc-args <STR>`: Extra arguments passed to FastQC (e.g., `"--adapters adapter_list.txt"`).
- `--multiqc-args <STR>`: Extra arguments passed to MultiQC.

### Example

```bash
uv run bioanalyze omics rna_seq run -c config.json
```

For non-model organisms, you can provide an assembly accession instead of a species name:

```bash
uv run bioanalyze omics rna_seq run \
  --input ./raw_data \
  --output ./results \
  --design ./design.csv \
  --assembly GCA_013347765.1
```

When `--species` is provided, the CLI first searches matching genomes via `genomepy.search()`, displays the candidates, and prompts you to choose one before downloading.

## Python API

### `RNASeqPipeline`

```python
from bio_analyze_omics.rna_seq.pipeline import RNASeqPipeline

pipeline = RNASeqPipeline(
    config_path="config.json",
    design_path="design.csv",
    output_dir="./results"
)

pipeline.run()
```

**plot() Arguments**:

<ParamTable params-path="omics/run_api" />
