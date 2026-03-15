---
---

# PCA Plot

Visualize sample distribution in principal component space, supporting automatic clustering ellipses.

> **Note**: `PCAPlot` now inherits from `ScatterPlot`, supporting all scatter plot arguments.

## CLI Usage

**Command**: `pca`

### Arguments

<ParamTable params-path="plot/pca_cli" />

### Example

```bash
bio-analyze plot pca counts.csv --transpose --hue Group --cluster
```

## Python API

### `PCAPlot`

```python
from bio_analyze_plot.plots import PCAPlot

pca = PCAPlot(theme="science")
pca.plot(
    data=counts,
    transpose=True,
    hue=["Ctrl", "Ctrl", "Treat", "Treat"],
    cluster=True,
    output="pca.png"
)
```

**plot() Arguments**:

<ParamTable params-path="plot/pca_api" />

