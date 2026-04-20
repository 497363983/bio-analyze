---
---

# de

Differential expression analysis using PyDESeq2.

## CLI Usage

**Command**: `de`

### Arguments

<ParamTable params-path="omics/rna_seq_de_cli" />

### Example

```bash
uv run bioanalyze omics rna_seq de -i counts.csv -d design.csv -o ./de_results --contrast "condition,Treat,Ctrl"
```
