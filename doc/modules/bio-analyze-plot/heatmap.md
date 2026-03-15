---
---

# Heatmap

Visualize gene expression or other matrix data clustering.

## CLI Usage

**Command**: `heatmap`

### Arguments

<ParamTable params-path="plot/heatmap_cli" />

### Example

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

**plot() Arguments**:

<ParamTable params-path="plot/heatmap_api" />