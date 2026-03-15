---
---

# 染色体分布图 (Chromosome Plot)

展示全基因组染色体上的 Read 密度分布。常用于与 `rna_seq` 流程结合展示正负链覆盖度。

## 命令行用法

**命令**: `chromosome`

### 关键参数

<ParamTable params-path="plot/chromosome_cli" />

### 示例

```bash
bio-analyze plot chromosome coverage.csv
```

## Python API

### `ChromosomePlot`

```python
from bio_analyze_plot.plots import ChromosomePlot

plotter = ChromosomePlot(theme="nature")
plotter.plot(
    data=df,
    chrom_col="chrom",
    pos_col="pos",
    pos_counts_col="pos_counts",
    neg_counts_col="neg_counts",
    output="chrom.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/chromosome_api" />
