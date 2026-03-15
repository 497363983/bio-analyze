---
---

# PCA 图 (PCA Plot)

可视化样本在主成分空间的分布，支持自动绘制聚类置信椭圆。

> **注意**: `PCAPlot` 目前继承自 `ScatterPlot`，因此支持散点图的所有参数。

## 命令行用法

**命令**: `pca`

### 关键参数

<ParamTable params-path="plot/pca_cli" />

### 示例

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

**plot() 参数**:

<ParamTable params-path="plot/pca_api" />
