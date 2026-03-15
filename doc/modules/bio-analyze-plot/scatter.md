---
---

# Scatter Plot

Display relationship between two variables, supporting confidence ellipses.

## CLI Usage

**Command**: `scatter`

### Arguments

<ParamTable params-path="plot/scatter_cli" />

### Example

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

**plot() Arguments**:

<ParamTable params-path="plot/scatter_api" />

