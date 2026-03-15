---
---

# 柱状图 (Bar Plot)

支持带误差棒（SD/SE/CI）和显著性标记的柱状图。

## 命令行用法

**命令**: `bar`

### 关键参数

<ParamTable params-path="plot/bar_cli" />

### 示例

```bash
bio-analyze plot bar data.csv -x Group -y Value --error-bar-type SD --significance "A,B"
```

## Python API

### `BarPlot`

```python
from bio_analyze_plot.plots import BarPlot

plotter = BarPlot(theme="nature")
plotter.plot(
    data=df,
    x="Group",
    y="Value",
    error_bar_type="SD",
    significance=[("A", "B")],
    output="bar.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/bar_api" />

