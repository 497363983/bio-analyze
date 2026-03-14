# bio-analyze-plot

**bio-analyze-plot** is the professional plotting module in the `bio-analyze` toolkit. Built on `matplotlib` and `seaborn`, it aims to generate comprehensive statistical charts and supports flexible theme customization.

## ✨ Core Features

- **Customizable Themes**: Built-in themes serve as a starting point, with full support for custom configurations (fonts, sizes, colors, etc.).
- **Broad Data Support**: Supports `.csv`, `.tsv`, `.txt`, `.xlsx`, and `.xls` formats; specify Excel sheets via `--sheet`.
- **Multi-Format Export**: Supports `png`, `pdf`, `svg`, `jpg`, `tiff`, and more.
- **LaTeX Support**: Automatically parses LaTeX formulas in axis labels (e.g., `$y = \sin(x)$`).
- **Unified CLI**: All plots can be called via a unified command-line interface.

## 📊 Supported Plots

### 1. Volcano Plot

Used to display the distribution of differentially expressed genes (DEGs), visually showing significantly upregulated and downregulated genes.

- **Command**: `volcano`
- **Key Parameters**:
  - `-x`: log2 Fold Change column name (default: "log2FoldChange")
  - `-y`: P-value column name (default: "pvalue")
  - `--fc-cutoff`: Fold Change threshold
  - `--p-cutoff`: P-value threshold
  - `--labels`: Custom labels (e.g., `{"up": "Up", "down": "Down", "ns": "NS"}`)

### 2. Bar Plot

Supports bar charts with error bars (SD/SE/CI) and significance markers.

- **Command**: `bar`
- **Key Parameters**:
  - `--error-bar-type`: Error bar type (`SD`, `SE`, `CI`).
  - `--error-bar-ci`: Confidence level for `CI` (default 95).
  - `--significance`: Pairs of groups to mark significance, e.g., "Control,Treated".
  - `--test`: Significance test method (`t-test_ind`, `t-test_welch`, `Mann-Whitney`, etc.).
  - `--text-format`: Significance marker format (`star`, `full`, `simple`, `pvalue`).

### 3. Box Plot

Displays data distribution, supports overlaying SwarmPlot and significance markers.

- **Command**: `box`
- **Key Parameters**:
  - `-x`: Grouping column (Categorical)
  - `-y`: Value column (Numerical)
  - `--hue`: Color grouping column
  - `--add-swarm`: Overlay swarm plot.
  - `--significance`: Significance marker pairs.

### 4. Heatmap

Cluster heatmap for gene expression or other matrix data.

- **Command**: `heatmap`
- **Key Parameters**:
  - `--cluster-rows` / `--cluster-cols`: Cluster rows/cols.
  - `--z-score`: Z-score normalization for rows (0) or cols (1).

### 5. PCA Plot

Principal Component Analysis plot, supports automatic clustering ellipses.

- **Command**: `pca`
- **Key Parameters**:
  - `--transpose`: Transpose matrix (if input is Gene x Sample, usually need transpose to Sample x Gene).
  - `--hue`: Sample grouping column.
  - `--cluster`: Show clustering ellipses.

### 6. Line Plot

For time series or trend data.

- **Command**: `line`
- **Key Parameters**:
  - `--hue`: Grouping column.

### 7. Pie Chart

Displays proportions of categorical data.

- **Command**: `pie`
- **Key Parameters**:
  - `--explode`: Distance to explode sectors.
  - `--autopct`: Percentage format (default "%1.1f%%").

### 8. Chromosome Distribution Plot

Displays Reads density distribution across the genome chromosomes.

- **Command**: `chromosome`
- **Note**: Usually used with `rna_seq` pipeline to show positive/negative strand coverage.

### 9. GSEA Enrichment Plot

Displays GSEA Enrichment Score trend.

- **Command**: `gsea`
- **Key Parameters**:
  - `--rank`: Rank value column.
  - `--score`: Running ES column.
  - `--nes`: Normalized Enrichment Score.
  - `--pvalue` / `--fdr`: Statistical significance metrics.

## 🎨 Themes

Support custom themes via JSON files or Python code.

### Built-in Themes

```bash
# Nature style
bioanalyze plot volcano result.csv --theme nature

# Science style
bioanalyze plot volcano result.csv --theme science
```

### Custom Theme (JSON)

Create `my_theme.json`:

```json
{
  "name": "dark_presentation",
  "style": "darkgrid",
  "context": "talk",
  "font": "Arial",
  "rc_params": {
    "lines.linewidth": 2.5,
    "axes.labelsize": 14
  }
}
```

Usage: `bioanalyze plot volcano ... --theme ./my_theme.json`

## 📦 Python API

All plots can be called directly via Python classes.

### Basic Usage

```python
import pandas as pd
from bio_analyze_plot.plots import VolcanoPlot, PCAPlot

# 1. Volcano Plot
df = pd.read_csv("de_results.csv")
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

# 2. PCA Plot
counts = pd.read_csv("counts.csv", index_col=0)
pca = PCAPlot(theme="science")
pca.plot(
    data=counts,
    transpose=True,  # If input is Gene x Sample
    hue=["Control", "Control", "Treat", "Treat"],
    cluster=True,
    output="pca.png"
)
```

## 💻 Development

Unit test outputs are in `packages/plot/tests/output`.

```bash
pytest packages/plot/tests
```
