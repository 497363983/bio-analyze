---
---

# align

Align reads to reference genome using STAR.

## CLI Usage

**Command**: `align`

### Arguments

<ParamTable params-path="omics/rna_seq_align_cli" />

### Example

```bash
uv run bioanalyze omics rna_seq align -i ./clean_data -o ./align_results --fasta genome.fa --gtf genome.gtf
```
