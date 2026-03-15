---
---

# 箱线图 (Box Plot)

用于展示数据分布，支持叠加散点图（SwarmPlot）及显著性标记。

## 命令行用法

**命令**: `box`

### 关键参数

<ParamTable params-path="plot/box_cli" />

### 示例

```bash
bio-analyze plot box data.csv -x Group -y Value --add-swarm
```

## Python API

### `BoxPlot`

```python
from bio_analyze_plot.plots import BoxPlot

plotter = BoxPlot(theme="nature")
plotter.plot(
    data=df,
    x="Group",
    y="Value",
    add_swarm=True,
    significance=[("Ctrl", "Treat")],
    output="box.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/box_api" />`
