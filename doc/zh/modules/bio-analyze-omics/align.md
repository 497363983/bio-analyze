---
---

# align

使用 STAR 将 reads 比对到参考基因组。

## 命令行用法

**命令**: `align`

### 关键参数

<ParamTable params-path="omics/rna_seq_align_cli" />

### 示例

```bash
uv run bioanalyze omics rna_seq align -i ./clean_data -o ./align_results --fasta genome.fa --gtf genome.gtf
```
