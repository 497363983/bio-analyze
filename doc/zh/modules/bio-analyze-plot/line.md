---
---

# 折线图 (Line Plot)

展示时间序列或趋势数据，支持平滑拟合及误差带。

## 命令行用法

**命令**: `line`

### 关键参数

<ParamTable params-path="plot/line_cli" />

### 示例

```bash
# 平滑曲线 + 误差棒
bio-analyze plot line time_series.csv -x Time -y Value --hue Group --smooth --error-bar-type SD
```

## Python API

### `LinePlot`

```python
from bio_analyze_plot.plots import LinePlot

plotter = LinePlot(theme="nature")
plotter.plot(
    data=df,
    x="Time",
    y="Value",
    hue="Group",
    smooth=True,
    error_bar_type="SE",
    output="line.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/line_api" />

