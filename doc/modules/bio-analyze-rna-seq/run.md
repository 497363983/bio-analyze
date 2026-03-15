---
---

# run

Run the complete RNA-Seq pipeline.

## CLI Usage

**Command**: `run`

### Arguments

<ParamTable params-path="rna_seq/run_cli" />

### Advanced QC Options

- `--fastqc-args <STR>`: Extra arguments passed to FastQC (e.g., `"--adapters adapter_list.txt"`).
- `--multiqc-args <STR>`: Extra arguments passed to MultiQC.

### Example

```bash
uv run bioanalyze rna-seq run -c config.json
```

## Python API

### `RNASeqPipeline`

```python
from bio_analyze_rna_seq.pipeline import RNASeqPipeline

pipeline = RNASeqPipeline(
    config_path="config.json",
    design_path="design.csv",
    output_dir="./results"
)

pipeline.run()
```

**plot() Arguments**:

<ParamTable params-path="rna_seq/run_api" />
