---
---

# Pie Chart

Display proportions of categorical data.

## CLI Usage

**Command**: `pie`

### Arguments

<ParamTable params-path="plot/pie_cli" />

### Example

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

**plot() Arguments**:

<ParamTable params-path="plot/pie_api" />
