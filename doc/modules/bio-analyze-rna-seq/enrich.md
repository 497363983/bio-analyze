---
---

# enrich

GO/KEGG enrichment analysis using gseapy.

## CLI Usage

**Command**: `enrich`

### Arguments

<ParamTable params-path="rna_seq/enrich_cli" />

### Example

```bash
uv run bioanalyze rna-seq enrich -i deg_list.txt -o ./enrich_results -s "Homo sapiens"
```
