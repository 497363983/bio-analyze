---
---

# GSEA 富集图 (GSEA Plot)

展示 GSEA 分析的 Enrichment Score (ES) 变化趋势。

## 命令行用法

**命令**: `gsea`

### 关键参数

<ParamTable params-path="plot/gsea_cli" />

### 示例

```bash
bio-analyze plot gsea gsea_result.csv --rank Rank --score ES
```

## Python API

### `GSEAPlot`

```python
from bio_analyze_plot.plots import GSEAPlot

plotter = GSEAPlot(theme="nature")
plotter.plot(
    data=df,
    rank="Rank",
    score="ES",
    nes=1.5,
    pvalue=0.01,
    output="gsea.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/gsea_api" />

