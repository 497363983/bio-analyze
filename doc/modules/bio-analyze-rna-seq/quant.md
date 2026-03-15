---
---

# quant

Quantify transcript expression using Salmon.

## CLI Usage

**Command**: `quant`

### Arguments

<ParamTable params-path="rna_seq/quant_cli" />

### Example

```bash
uv run bioanalyze rna-seq quant -i ./clean_data -o ./quant_results --fasta transcripts.fa
```

## Python API

### `QuantManager`

```python
from bio_analyze_rna_seq.quant import QuantManager
from pathlib import Path

reads = {
    "sample1": {"R1": "sample1_1.fq.gz", "R2": "sample1_2.fq.gz"}
}
reference = {
    "fasta": Path("genome.fa"),
    "gtf": Path("genes.gtf")
}

manager = QuantManager(
    reads=reads,
    reference=reference,
    output_dir=Path("./quant_results"),
    threads=8
)

# Returns merged counts matrix (DataFrame)
counts_df = manager.run()
```
