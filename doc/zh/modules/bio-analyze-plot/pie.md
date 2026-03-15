---
---

# 饼图 (Pie Chart)

展示类别数据的比例关系。

## 命令行用法

**命令**: `pie`

### 关键参数

<ParamTable params-path="plot/pie_cli" />

### 示例

```bash
bio-analyze plot pie data.csv -x Category -y Value --explode 0.1
```

## Python API

### `PiePlot`

```python
from bio_analyze_plot.plots import PiePlot

plotter = PiePlot(theme="nature")
plotter.plot(
    data=df,
    x="Category",
    y="Value",
    output="pie.png"
)
```

**plot() 参数**:

<ParamTable params-path="plot/pie_api" />

