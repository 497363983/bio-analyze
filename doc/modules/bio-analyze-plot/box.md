---
---

# Box Plot

Display data distribution, support overlaying SwarmPlot and significance markers.

## CLI Usage

**Command**: `box`

### Arguments

<ParamTable params-path="plot/box_cli" />

### Example

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

**plot() Arguments**:

<ParamTable params-path="plot/box_api" />
