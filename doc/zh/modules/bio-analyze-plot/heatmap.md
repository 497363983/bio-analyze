---
---

# 热图 (Heatmap)

用于基因表达量或其他矩阵数据的聚类可视化。

## 命令行用法

**命令**: `heatmap`

### 关键参数

<ParamTable params-path="plot/heatmap_cli" />

### 示例

```bash
bio-analyze plot heatmap expression.csv --cluster-rows --z-score 0
```

## Python API

### `HeatmapPlot`

```python
from bio_analyze_plot.plots import HeatmapPlot

plotter = HeatmapPlot(theme="nature")
plotter.plot(
    data=df,
    cluster_rows=True,
    z_score=0,
    output="heatmap.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/heatmap_api" />
