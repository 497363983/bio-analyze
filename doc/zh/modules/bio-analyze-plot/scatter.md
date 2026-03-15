---
---

# 散点图 (Scatter Plot)

展示两个变量之间的关系，支持分组着色、形状映射及置信椭圆。

## 命令行用法

**命令**: `scatter`

### 关键参数

<ParamTable params-path="plot/scatter_cli" />

### 示例

```bash
bio-analyze plot scatter data.csv -x GeneA -y GeneB --hue Group --add-ellipse
```

## Python API

### `ScatterPlot`

```python
from bio_analyze_plot.plots import ScatterPlot

plotter = ScatterPlot(theme="nature")
plotter.plot(
    data=df,
    x="GeneA",
    y="GeneB",
    hue="Group",
    add_ellipse=True,
    output="scatter.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/scatter_api" />