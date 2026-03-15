---
---

# qc

使用 fastp 和 FastQC 对 FASTQ 文件进行质量控制。

## 命令行用法

**命令**: `qc`

### 关键参数

<ParamTable params-path="rna_seq/qc_cli" />

### 示例

```bash
uv run bioanalyze rna-seq qc -i ./raw_data -o ./qc_results
```
