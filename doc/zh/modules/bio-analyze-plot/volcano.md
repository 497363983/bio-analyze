---
---

# 火山图 (Volcano Plot)

用于展示差异表达基因（DEG）分布，直观显示显著上调和下调的基因。

## 命令行用法

**命令**: `volcano`

### 关键参数

<ParamTable params-path="plot/volcano_cli" />

### 示例

```bash
bio-analyze plot volcano result.csv --fc-cutoff 1.5 --p-cutoff 0.05
```

## Python API

### `VolcanoPlot`

```python
from bio_analyze_plot.plots import VolcanoPlot

plotter = VolcanoPlot(theme="nature")
plotter.plot(
    data=df,
    x="log2FoldChange",
    y="padj",
    fc_cutoff=1.5,
    p_cutoff=0.05,
    title="Differential Expression",
    output="volcano.pdf"
)
```

**plot() 参数**:

<ParamTable params-path="plot/volcano_api" />
