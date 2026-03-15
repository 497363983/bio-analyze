---
---

# Line Plot

Display time series or trend data, supporting smooth fitting and error bars.

## CLI Usage

**Command**: `line`

### Arguments

<ParamTable params-path="plot/line_cli" />

### Example

```bash
# Smooth curve + error bars
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

**plot() Arguments**:

<ParamTable params-path="plot/line_api" />
