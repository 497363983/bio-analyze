# bio-analyze-plot

**bio-analyze-plot** 是 `bio-analyze` 工具箱中的专业绘图模块。它基于 `matplotlib` 和 `seaborn` 构建，旨在生成各类生物信息学统计图表，并支持灵活的主题定制。

## ✨ 核心特性 (Features)

- **可定制主题**：提供内置主题作为基础，同时支持完全自定义字体、字号、线条粗细和配色方案。
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

用于展示时间序列或趋势数据。

- **命令**: `line`
- **关键参数**:
  - `--hue`: 分组列，不同组显示不同颜色的线条。

### 7. 饼图 (Pie Chart)

展示分类数据的占比。

- **命令**: `pie`
- **关键参数**:
  - `--explode`: 扇区炸开的距离。
  - `--autopct`: 百分比显示格式 (默认 "%1.1f%%")。

### 8. 染色体分布图 (Chromosome Distribution Plot)

展示 Reads 在全基因组染色体上的分布密度。

- **命令**: `chromosome`
- **说明**: 通常配合 `rna_seq` 流程使用，展示正负链的 Reads 覆盖度。

### 9. GSEA 富集图 (GSEA Enrichment Plot)

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

## 💻 开发 (Development)

单元测试输出位于 `packages/plot/tests/output` 目录。

```bash
pytest packages/plot/tests
```
