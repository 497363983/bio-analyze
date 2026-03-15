---
---

# GSEA Enrichment Plot

Display Enrichment Score (ES) trend for GSEA analysis.

## CLI Usage

**Command**: `gsea`

### Arguments

<ParamTable params-path="plot/gsea_cli" />

### Example

```bash
bio-analyze plot gsea gsea_result.csv --rank Rank --score ES
```

## Python API

### `GSEAPlot`

```python
from bio_analyze_plot.plots import GSEAPlot

plotter = GSEAPlot(theme="nature")
plotter.plot(
    data=df,
    rank="Rank",
    score="ES",
    nes=1.5,
    pvalue=0.01,
    output="gsea.png"
)
```

**plot() Arguments**:

<ParamTable params-path="plot/gsea_api" />
