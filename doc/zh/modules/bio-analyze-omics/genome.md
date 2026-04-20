---
---

# genome

下载参考基因组和注释文件。

## 命令行用法

**命令**: `genome`

### 关键参数

<ParamTable params-path="omics/rna_seq_genome_cli" />

### 示例

```bash
uv run bioanalyze omics rna_seq genome -s "Homo sapiens" -o ./reference
```

也可以直接使用组装号下载：

```bash
uv run bioanalyze omics rna_seq genome --assembly GCA_013347765.1 -o ./reference
```

当传入 `--species` 时，命令会先搜索候选基因组，并提示你选择要下载的目标结果。
