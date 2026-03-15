---
---

# Volcano Plot

Visualize differential expression gene (DEG) distribution, intuitively showing significantly upregulated and downregulated genes.

## CLI Usage

**Command**: `volcano`

### Arguments

<ParamTable params-path="plot/volcano_cli" />

### Example

```bash
bio-analyze plot volcano result.csv --fc-cutoff 1.5 --p-cutoff 0.05
```

## Python API

### `VolcanoPlot`

```python
from bio_analyze_plot.plots import VolcanoPlot

plotter = VolcanoPlot(theme="nature")
plotter.plot(
    data=df,
    x="log2FoldChange",
    y="padj",
    fc_cutoff=1.5,
    p_cutoff=0.05,
    title="Differential Expression",
    output="volcano.pdf"
)
```

**plot() Arguments**:

<ParamTable params-path="plot/volcano_api" />

