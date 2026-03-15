---
---

# de

使用 PyDESeq2 进行差异表达分析。

## 命令行用法

**命令**: `de`

### 关键参数

<ParamTable params-path="rna_seq/de_cli" />

### 示例

```bash
uv run bioanalyze rna-seq de -i counts.csv -d design.csv -o ./de_results --contrast "condition,Treat,Ctrl"
```
