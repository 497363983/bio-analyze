---
---

# genome

Download reference genome and annotation files.

## CLI Usage

**Command**: `genome`

### Arguments

<ParamTable params-path="omics/rna_seq_genome_cli" />

### Example

```bash
uv run bioanalyze omics rna_seq genome -s "Homo sapiens" -o ./reference
```

You can also download by assembly accession:

```bash
uv run bioanalyze omics rna_seq genome --assembly GCA_013347765.1 -o ./reference
```

When you pass `--species`, the command first searches candidate genomes and prompts you to pick the desired result before downloading.
