---
---

# enrich

GO/KEGG enrichment analysis using gseapy.

## CLI Usage

**Command**: `enrich`

### Arguments

<ParamTable params-path="omics/rna_seq_enrich_cli" />

### Example

```bash
uv run bioanalyze omics rna_seq enrich -i deg_list.txt -o ./enrich_results -s "Homo sapiens"
```
