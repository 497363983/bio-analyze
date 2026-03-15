---
---

# de

Differential expression analysis using PyDESeq2.

## CLI Usage

**Command**: `de`

### Arguments

<ParamTable params-path="rna_seq/de_cli" />

### Example

```bash
uv run bioanalyze rna-seq de -i counts.csv -d design.csv -o ./de_results --contrast "condition,Treat,Ctrl"
```
