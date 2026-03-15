---
---

# enrich

使用 gseapy 进行 GO/KEGG 富集分析。

## 命令行用法

**命令**: `enrich`

### 关键参数

<ParamTable params-path="rna_seq/enrich_cli" />

### 示例

```bash
uv run bioanalyze rna-seq enrich -i deg_list.txt -o ./enrich_results -s "Homo sapiens"
```
