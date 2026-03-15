---
---

# Bar Plot

Support bar plots with error bars (SD/SE/CI) and significance markers.

## CLI Usage

**Command**: `bar`

### Arguments

<ParamTable params-path="plot/bar_cli" />

### Example

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

**plot() Arguments**:

<ParamTable params-path="plot/bar_api" />
