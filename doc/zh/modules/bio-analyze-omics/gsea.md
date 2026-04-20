---
---

# gsea

进行 GSEA 富集分析。

## 命令行用法

**命令**: `gsea`

### 关键参数

<ParamTable params-path="omics/rna_seq_gsea_cli" />

### 示例

```bash
uv run bioanalyze omics rna_seq gsea -i ranked_genes.csv -o ./gsea_results -s "Homo sapiens"
```
