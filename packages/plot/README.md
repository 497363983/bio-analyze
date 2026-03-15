# bio-analyze-plot

**bio-analyze-plot** 是 `bio-analyze` 工具箱中的专业绘图模块。它基于 `matplotlib` 和 `seaborn` 构建，旨在生成达到出版级要求（Publication-Ready）的统计图表，并支持一键切换 `Nature`、`Science` 等期刊主题。

## ✨ 核心特性 (Features)

- **出版级主题**：内置 `nature`、`science` 及 `default` 主题，自动调整字体、字号、线条粗细和配色。
- **广泛的数据支持**：支持 `.csv`、`.tsv`、`.txt`、`.xlsx` 及 `.xls` 格式，可通过 `--sheet` 指定 Excel 工作表。
- **多格式导出**：支持 `png`、`pdf`、`svg`、`jpg`、`tiff` 等多种图像格式。
- **中文注释**：代码注释全中文，便于开发者阅读和二次开发。
- **LaTeX 支持**：自动解析坐标轴标签中的 LaTeX 公式（如 `$y = \sin(x)$`）。
- **统一 CLI**：所有图表均可通过统一的命令行接口调用。

## 📊 支持的图表 (Supported Plots)

### 1. 火山图 (Volcano Plot)

用于展示差异表达基因（DEG）分布，直观显示显著上调和下调的基因。

- **命令**: `volcano`
- **关键参数**:
  - `-x`: log2 Fold Change 列名 (默认: "log2FoldChange")
  - `-y`: P-value 列名 (默认: "pvalue")
  - `--fc-cutoff`: Fold Change 阈值
  - `--p-cutoff`: P-value 阈值
  - `--labels`: 自定义标签（如 `{"up": "Up", "down": "Down", "ns": "NS"}`）

### 2. 柱状图 (Bar Plot)

支持带有误差棒（SD/SE/CI）和显著性标记的柱状图。

- **命令**: `bar`
- **关键参数**:
  - `--error-bar-type`: 误差棒类型，可选 `SD` (标准差), `SE` (标准误), `CI` (置信区间)。
  - `--error-bar-ci`: 当类型为 `CI` 时的置信度（默认 95）。
  - `--significance`: 指定需要标注显著性的组别对，例如 "Control,Treated"。
  - `--test`: 显著性检验方法，支持 `t-test_ind`, `t-test_welch`, `Mann-Whitney` 等。
  - `--text-format`: 显著性标记格式 (`star`, `full`, `simple`, `pvalue`)。

### 3. 箱线图 (Box Plot)

展示数据分布，支持叠加 SwarmPlot 散点和显著性标记。

- **命令**: `box`
- **关键参数**:
  - `-x`: 分组列 (Categorical)
  - `-y`: 数值列 (Numerical)
  - `--hue`: 颜色分组列
  - `--add-swarm`: 是否叠加蜂群图 (Swarmplot) 显示所有数据点。
  - `--significance`: 显著性标注组别对。

### 4. 热图 (Heatmap)

用于展示基因表达量或其他矩阵数据的聚类热图。

- **命令**: `heatmap`
- **关键参数**:
  - `--cluster-rows` / `--cluster-cols`: 是否对行/列进行聚类。
  - `--z-score`: 对行 (0) 或列 (1) 进行 Z-score 标准化。

### 5. 主成分分析图 (PCA Plot)

展示样本在主成分空间的分布，支持自动聚类圈选。

- **命令**: `pca`
- **关键参数**:
  - `--transpose`: 是否转置矩阵（如果输入是 基因x样本，通常需要转置为 样本x基因）。
  - `--hue`: 样本分组列。
  - `--cluster`: 是否显示聚类椭圆。

### 6. 折线图 (Line Plot)

用于展示时间序列或趋势数据，支持平滑拟合和误差棒。

- **命令**: `line`
- **关键参数**:
  - `--hue`: 分组列，不同组显示不同颜色的线条。
  - `--smooth`: 启用平滑曲线拟合（B-spline）。
  - `--smooth-points`: 平滑插值点数（默认 300）。
  - `--error-bar-type`: 误差棒类型 (`SD`, `SE`, `CI`)。
  - `--error-bar-ci`: 置信区间大小。
  - `--error-bar-capsize`: 误差棒横线宽度。
  - `--markers`: 显示原始数据点标记。

### 7. 散点图 (Scatter Plot)

展示两个变量之间的关系，支持置信椭圆。

- **命令**: `scatter`
- **关键参数**:
  - `--x`, `--y`: X/Y 轴列名。
  - `--hue`: 颜色分组列。
  - `--size`: 点大小映射列。
  - `--style`: 点形状映射列。
  - `--add-ellipse`: 为每个分组绘制置信椭圆。
  - `--ellipse-std`: 椭圆标准差倍数（默认 2.0）。

### 8. 饼图 (Pie Chart)

展示分类数据的占比。

- **命令**: `pie`
- **关键参数**:
  - `--explode`: 扇区炸开的距离。
  - `--autopct`: 百分比显示格式 (默认 "%1.1f%%")。

### 9. 染色体分布图 (Chromosome Distribution Plot)

展示 Reads 在全基因组染色体上的分布密度。

- **命令**: `chromosome`
- **说明**: 通常配合 `rna_seq` 流程使用，展示正负链的 Reads 覆盖度。

### 10. GSEA 富集图 (GSEA Enrichment Plot)

展示 GSEA 分析的富集评分（Enrichment Score）走势。

- **命令**: `gsea`
- **关键参数**:
  - `--rank`: 排序值列名。
  - `--score`: Running ES 列名。
  - `--nes`: 标准化富集评分（显示在标题中）。
  - `--pvalue` / `--fdr`: 统计显著性指标。

## 🎨 主题定制 (Themes)

支持通过 JSON 文件或 Python 代码自定义绘图主题。

### 使用内置主题

```bash
# 使用 Nature 风格
bioanalyze plot volcano result.csv --theme nature

# 使用 Science 风格
bioanalyze plot volcano result.csv --theme science
```

### 自定义主题 (JSON)

创建 `my_theme.json`:

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

使用: `bioanalyze plot volcano ... --theme ./my_theme.json`

## 📦 Python API

所有图表均可通过 Python 类直接调用，支持更灵活的定制。

### 基础用法

```python
import pandas as pd
from bio_analyze_plot.plots import VolcanoPlot, PCAPlot

# 1. 绘制火山图
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

# 2. 绘制 PCA 图
counts = pd.read_csv("counts.csv", index_col=0)
pca = PCAPlot(theme="science")
pca.plot(
    data=counts,
    transpose=True,  # 如果输入是 基因x样本
    hue=["Control", "Control", "Treat", "Treat"], # 样本分组
    cluster=True,    # 绘制置信椭圆
    output="pca.png"
)
```

### 图表类索引

#### `VolcanoPlot`
- **plot() 参数**:
  - `data` (DataFrame): 数据源。
  - `x`, `y` (str): 列名。
  - `log_y` (bool): 是否对 y 取 -log10 (默认 True)。
  - `fc_cutoff`, `p_cutoff` (float): 阈值线。
  - `labels` (dict): 图例标签 (如 `{"up": "Up", "down": "Down", "ns": "NS"}`)。

#### `HeatmapPlot`
- **plot() 参数**:
  - `cluster_rows`, `cluster_cols` (bool): 是否聚类。
  - `z_score` (int): 0=行标准化, 1=列标准化, None=不标准化。
  - `cmap` (str): 颜色映射 (默认 "vlag")。

#### `BoxPlot`
- **plot() 参数**:
  - `significance` (list[tuple]): 显著性标记对 (如 `[("Ctrl", "Treat")]`)。
  - `test` (str): 检验方法 (默认 "t-test_ind")。
  - `add_swarm` (bool): 是否叠加散点。

#### `LinePlot`
- **plot() 参数**:
  - `smooth` (bool): 启用平滑曲线。
  - `error_bar_type` (str): 误差棒类型。
  - `markers` (bool/list): 数据点标记。

#### `ScatterPlot`
- **plot() 参数**:
  - `add_ellipse` (bool): 绘制置信椭圆。
  - `ellipse_std` (float): 椭圆标准差。
  - `style`, `size` (str): 样式/大小映射列。

#### `PCAPlot` (继承自 ScatterPlot)
- **plot() 参数**:
  - `transpose` (bool): 是否转置输入矩阵。
  - `n_components` (int): 主成分数。
  - `cluster` (bool): 是否绘制置信椭圆。

#### `ChromosomeDistributionPlot`
- **plot() 参数**:
  - `chrom_col`, `pos_col`: 染色体和位置列名。
  - `pos_counts_col`, `neg_counts_col`: 正负链计数列。
  - `max_chroms` (int): 显示的最大染色体数。

#### `GSEAPlot`
- **plot() 参数**:
  - `rank`, `score`: 排名和分数数据列。
  - `nes`, `pvalue`, `fdr`: 统计指标（显示在图中）。

## 💻 开发 (Development)

单元测试输出位于 `packages/plot/tests/output` 目录。

```bash
pytest packages/plot/tests
```
