# bio-analyze-plot

**bio-analyze-plot** is the professional plotting module in the `bio-analyze` toolkit. Built on `matplotlib` and `seaborn`, it aims to generate various bioinformatics statistical charts and supports flexible theme customization.

## ✨ Core Features (Features)

- **Customizable Themes**: Provides built-in themes as a base, while supporting full customization of fonts, sizes, line widths, and color schemes.
- **Extensive Data Support**: Supports `.csv`, `.tsv`, `.txt`, `.xlsx`, and `.xls` formats, specifying Excel sheets via `--sheet`.
- **Multi-Format Export**: Supports `png`, `pdf`, `svg`, `jpg`, `tiff`, and other image formats.
- **Chinese Comments**: Code comments are fully in Chinese, facilitating developer reading and secondary development.
- **LaTeX Support**: Automatically parses LaTeX formulas in axis labels (e.g., `$y = \sin(x)$`).
- **Unified CLI**: All charts can be called via a unified command-line interface.

## 📊 Supported Plots

### 1. Volcano Plot

Used to display differential expression gene (DEG) distribution, intuitively showing significantly upregulated and downregulated genes.

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
  - `--error-bar-type`: Error bar type, options `SD` (Standard Deviation), `SE` (Standard Error), `CI` (Confidence Interval).
  - `--error-bar-ci`: Confidence level when type is `CI` (default 95).
  - `--significance`: Specify group pairs needing significance annotation, e.g., "Control,Treated".
  - `--test`: Significance test method, supports `t-test_ind`, `t-test_welch`, `Mann-Whitney`, etc.
  - `--text-format`: Significance marker format (`star`, `full`, `simple`, `pvalue`).

### 3. Box Plot

Displays data distribution, supports overlaying SwarmPlot scatter points and significance markers.

- **Command**: `box`
- **Key Parameters**:
  - `-x`: Grouping column (Categorical)
  - `-y`: Value column (Numerical)
  - `--hue`: Color grouping column
  - `--add-swarm`: Whether to overlay swarm plot to show all data points.
  - `--significance`: Significance annotation group pairs.

### 4. Heatmap

Used to display clustering heatmaps of gene expression or other matrix data.

- **Command**: `heatmap`
- **Key Parameters**:
  - `--cluster-rows` / `--cluster-cols`: Whether to cluster rows/cols.
  - `--z-score`: Z-score standardization on rows (0) or cols (1).

### 5. PCA Plot

Displays sample distribution in principal component space, supporting automatic clustering ellipse.

- **Command**: `pca`
- **Key Parameters**:
  - `--transpose`: Whether to transpose matrix (if input is Gene x Sample, usually need to transpose to Sample x Gene).
  - `--hue`: Sample grouping column.
  - `--cluster`: Whether to display clustering ellipses.

### 6. Line Plot

Used to display time series or trend data.

- **Command**: `line`
- **Key Parameters**:
  - `--hue`: Grouping column, different groups display lines in different colors.

### 7. Pie Chart

Displays proportions of categorical data.

- **Command**: `pie`
- **Key Parameters**:
  - `--explode`: Distance to explode sectors.
  - `--autopct`: Percentage display format (default "%1.1f%%").

### 8. Chromosome Distribution Plot

Displays Reads distribution density on whole genome chromosomes.

- **Command**: `chromosome`
- **Description**: Usually used with `rna_seq` pipeline to display Reads coverage on forward and reverse strands.

### 9. GSEA Enrichment Plot

Displays Enrichment Score trend in GSEA analysis.

- **Command**: `gsea`
- **Key Parameters**:
  - `--rank`: Ranking value column name.
  - `--score`: Running ES column name.
  - `--nes`: Normalized Enrichment Score (displayed in title).
  - `--pvalue` / `--fdr`: Statistical significance indicators.

## 🎨 Theme Customization (Themes)

Supports customizing plotting themes via JSON files or Python code.

### Using Built-in Themes

```bash
# Use Nature style
bioanalyze plot volcano result.csv --theme nature

# Use Science style
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

Use: `bioanalyze plot volcano ... --theme ./my_theme.json`

## 📦 Python API

All charts can be called directly via Python classes, supporting more flexible customization.

### Basic Usage

```python
import pandas as pd
from bio_analyze_plot.plots import VolcanoPlot, PCAPlot

# 1. Plot Volcano Plot
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

# 2. Plot PCA Plot
counts = pd.read_csv("counts.csv", index_col=0)
pca = PCAPlot(theme="science")
pca.plot(
    data=counts,
    transpose=True,  # If input is Gene x Sample
    hue=["Control", "Control", "Treat", "Treat"], # Sample grouping
    cluster=True,    # Plot confidence ellipses
    output="pca.png"
)
```

## 💻 Development

Unit test output is located in `packages/plot/tests/output` directory.

```bash
pytest packages/plot/tests
```
