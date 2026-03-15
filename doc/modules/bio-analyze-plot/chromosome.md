---
---

# Chromosome Distribution Plot

Display read density across whole genome chromosomes. Usually used with `rna_seq` pipeline to show positive/negative strand coverage.

## CLI Usage

**Command**: `chromosome`

### Arguments

<ParamTable params-path="plot/chromosome_cli" />

### Example

```bash
bio-analyze plot chromosome coverage.csv
```

## Python API

### `ChromosomePlot`

```python
from bio_analyze_plot.plots import ChromosomePlot

plotter = ChromosomePlot(theme="nature")
plotter.plot(
    data=df,
    chrom_col="chrom",
    pos_col="pos",
    pos_counts_col="pos_counts",
    neg_counts_col="neg_counts",
    output="chrom.png"
)
```

**plot() Arguments**:

<ParamTable params-path="plot/chromosome_api" />

