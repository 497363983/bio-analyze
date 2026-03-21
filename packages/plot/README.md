# bio-analyze-plot

[![PyPI Version](https://img.shields.io/pypi/v/bio-analyze-plot?label=PyPI&include_prereleases&sort=semver&logo=python)](https://pypi.org/project/bio-analyze-plot/)

**bio-analyze-plot** is the professional plotting module in the `bio-analyze` toolbox. Built on `matplotlib` and `seaborn`, it aims to generate publication-ready statistical charts and supports one-click switching between journal themes like `Nature` and `Science`.

## ✨ Features

- **Publication-Ready Themes**: Built-in `nature`, `science`, and `default` themes that automatically adjust fonts, font sizes, line widths, and color palettes.
- **Wide Data Support**: Supports `.csv`, `.tsv`, `.txt`, `.xlsx`, and `.xls` formats. Specific Excel sheets can be targeted via `--sheet`.
- **Multi-Format Export**: Supports various image formats including `png`, `pdf`, `svg`, `jpg`, and `tiff`.
- **LaTeX Support**: Automatically parses LaTeX formulas in axis labels (e.g., `$y = \sin(x)$`).
- **Unified CLI**: All charts can be invoked through a unified command-line interface.

## 📊 Supported Plots

### 1. Volcano Plot

Used to display the distribution of Differentially Expressed Genes (DEGs), intuitively showing significantly up-regulated and down-regulated genes.

- **Command**: `volcano`
- **Key Parameters**:
  - `-x`: log2 Fold Change column name (Default: "log2FoldChange")
  - `-y`: P-value column name (Default: "pvalue")
  - `--fc-cutoff`: Fold Change threshold
  - `--p-cutoff`: P-value threshold
  - `--labels`: Custom labels (e.g., `{"up": "Up", "down": "Down", "ns": "NS"}`)

### 2. Bar Plot

Supports bar charts with error bars (SD/SE/CI) and significance markers.

- **Command**: `bar`
- **Key Parameters**:
  - `--error-bar-type`: Error bar type. Options: `SD` (Standard Deviation), `SE` (Standard Error), `CI` (Confidence Interval).
  - `--error-bar-ci`: Confidence level when type is `CI` (Default: 95).
  - `--significance`: Specify group pairs for significance annotation, e.g., "Control,Treated".
  - `--test`: Significance test method. Supports `t-test_ind`, `t-test_welch`, `Mann-Whitney`, etc.
  - `--text-format`: Significance marker format (`star`, `full`, `simple`, `pvalue`).

### 3. Box Plot

Displays data distribution, supporting overlaid SwarmPlot scatter points and significance markers.

- **Command**: `box`
- **Key Parameters**:
  - `-x`: Grouping column (Categorical)
  - `-y`: Value column (Numerical)
  - `--hue`: Color grouping column
  - `--add-swarm`: Whether to overlay a Swarmplot to show all data points.
  - `--significance`: Group pairs for significance annotation.

### 4. Heatmap

Used to display clustered heatmaps of gene expression or other matrix data.

- **Command**: `heatmap`
- **Key Parameters**:
  - `--cluster-rows` / `--cluster-cols`: Whether to cluster rows/columns.
  - `--z-score`: Perform Z-score normalization on rows (0) or columns (1).

### 5. PCA Plot

Displays the distribution of samples in principal component space, supporting automatic clustering ellipses.

- **Command**: `pca`
- **Key Parameters**:
  - `--transpose`: Whether to transpose the matrix (if input is Genes x Samples, it usually needs to be transposed to Samples x Genes).
  - `--hue`: Sample grouping column.
  - `--cluster`: Whether to display clustering confidence ellipses.

### 6. Line Plot

Used to display time series or trend data, supporting smooth fitting and error bars.

- **Command**: `line`
- **Key Parameters**:
  - `--hue`: Grouping column; different groups are shown in different colors.
  - `--smooth`: Enable smooth curve fitting (B-spline).
  - `--smooth-points`: Number of interpolation points for smoothing (Default: 300).
  - `--error-bar-type`: Error bar type (`SD`, `SE`, `CI`).
  - `--error-bar-ci`: Confidence interval size.
  - `--error-bar-capsize`: Width of the error bar caps.
  - `--markers`: Display markers for original data points.

### 7. Scatter Plot

Displays the relationship between two variables, supporting confidence ellipses.

- **Command**: `scatter`
- **Key Parameters**:
  - `--x`, `--y`: X/Y axis column names.
  - `--hue`: Color grouping column.
  - `--size`: Column to map point sizes.
  - `--style`: Column to map point styles/shapes.
  - `--add-ellipse`: Draw confidence ellipses for each group.
  - `--ellipse-std`: Standard deviation multiplier for the ellipse (Default: 2.0).

### 8. Pie Chart

Displays the proportions of categorical data.

- **Command**: `pie`
- **Key Parameters**:
  - `--explode`: Distance to explode sectors.
  - `--autopct`: Percentage display format (Default: "%1.1f%%").

### 9. Chromosome Distribution Plot

Displays the distribution density of Reads across whole-genome chromosomes.

- **Command**: `chromosome`
- **Description**: Typically used with the `rna_seq` pipeline to show read coverage on positive and negative strands.

### 10. GSEA Enrichment Plot

Displays the Enrichment Score trend of GSEA analysis.

- **Command**: `gsea`
- **Key Parameters**:
  - `--rank`: Rank value column name.
  - `--score`: Running ES column name.
  - `--nes`: Normalized Enrichment Score (displayed in the title).
  - `--pvalue` / `--fdr`: Statistical significance metrics.

## 🎨 Themes

Supports customizing plotting themes via JSON files or Python code.

### Using Built-in Themes

```bash
# Use Nature style
bioanalyze plot volcano result.csv --theme nature

# Use Science style
bioanalyze plot volcano result.csv --theme science
```

### Custom Themes (JSON)

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

All charts can be invoked directly via Python classes, supporting more flexible customization.

### Basic Usage

```python
import pandas as pd
from bio_analyze_plot.plots import VolcanoPlot, PCAPlot

# 1. Plot Volcano
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

# 2. Plot PCA
counts = pd.read_csv("counts.csv", index_col=0)
pca = PCAPlot(theme="science")
pca.plot(
    data=counts,
    transpose=True,  # If input is Genes x Samples
    hue=["Control", "Control", "Treat", "Treat"], # Sample grouping
    cluster=True,    # Draw confidence ellipses
    output="pca.png"
)
```

### Chart Class Index

#### `VolcanoPlot`
- **plot() Parameters**:
  - `data` (DataFrame): Data source.
  - `x`, `y` (str): Column names.
  - `log_y` (bool): Whether to apply -log10 to y (Default: True).
  - `fc_cutoff`, `p_cutoff` (float): Threshold lines.
  - `labels` (dict): Legend labels (e.g., `{"up": "Up", "down": "Down", "ns": "NS"}`).

#### `HeatmapPlot`
- **plot() Parameters**:
  - `cluster_rows`, `cluster_cols` (bool): Whether to cluster.
  - `z_score` (int): 0=Row standardization, 1=Column standardization, None=No standardization.
  - `cmap` (str): Colormap (Default: "vlag").

#### `BoxPlot`
- **plot() Parameters**:
  - `significance` (list[tuple]): Pairs for significance markers (e.g., `[("Ctrl", "Treat")]`).
  - `test` (str): Test method (Default: "t-test_ind").
  - `add_swarm` (bool): Whether to overlay scatter points.

#### `LinePlot`
- **plot() Parameters**:
  - `smooth` (bool): Enable smooth curve.
  - `error_bar_type` (str): Error bar type.
  - `markers` (bool/list): Data point markers.

#### `ScatterPlot`
- **plot() Parameters**:
  - `add_ellipse` (bool): Draw confidence ellipses.
  - `ellipse_std` (float): Ellipse standard deviation.
  - `style`, `size` (str): Style/size mapping columns.

#### `PCAPlot` (Inherits from ScatterPlot)
- **plot() Parameters**:
  - `transpose` (bool): Whether to transpose the input matrix.
  - `n_components` (int): Number of principal components.
  - `cluster` (bool): Whether to draw confidence ellipses.

#### `ChromosomeDistributionPlot`
- **plot() Parameters**:
  - `chrom_col`, `pos_col`: Chromosome and position column names.
  - `pos_counts_col`, `neg_counts_col`: Positive and negative strand count columns.
  - `max_chroms` (int): Maximum number of chromosomes to display.

#### `GSEAPlot`
- **plot() Parameters**:
  - `rank`, `score`: Rank and score data columns.
  - `nes`, `pvalue`, `fdr`: Statistical metrics (displayed in the plot).

## 💻 Development

Unit test outputs are located in the `packages/plot/tests/output` directory.

```bash
pytest packages/plot/tests
```
