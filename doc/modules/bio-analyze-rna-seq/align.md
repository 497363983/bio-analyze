---
---

# align

Align reads to reference genome using STAR.

## CLI Usage

**Command**: `align`

### Arguments

<ParamTable params-path="rna_seq/align_cli" />

### Example

```bash
uv run bioanalyze rna-seq align -i ./clean_data -o ./align_results --fasta genome.fa --gtf genome.gtf
```
