# bio-analyze-plot

**bio-analyze-plot** 是 `bio-analyze` 工具箱中的专业绘图模块，旨在为生物信息学分析提供“发表级”（Publication-Ready）的图表生成功能。它基于 `matplotlib` 和 `seaborn` 构建，内置了 Nature 和 Science 等期刊的配色与样式主题，支持多种常见数据格式，并完美支持中文显示。

## ✨ 特性 (Features)

- **多主题支持**：一键切换 `nature`、`science` 或 `default` 风格，也支持加载用户自定义主题。
- **宽泛的数据格式**：支持读取 `.csv`、`.tsv`、`.txt`、`.xlsx` 和 `.xls` 文件。
- **中文友好**：自动检测并使用系统中的中文字体，无需繁琐配置。
- **LaTeX 支持**：默认支持在标题和轴标签中使用 LaTeX 数学公式（如 `$y = \sin(x)$`）。
- **灵活的 CLI**：通过命令行快速生成图表，支持丰富的参数调整。

## 📊 支持的图表 (Supported Plots)

### 1. 火山图 (Volcano Plot)

用于展示差异表达基因（DEG）结果，突出显示显著上调和下调的基因。

- **命令**: `volcano`
- **关键参数**:
  - `-x`: log2 Fold Change 列名 (默认: "log2FoldChange")
  - `-y`: P-value 列名 (默认: "pvalue")
  - `--fc-cutoff`: Fold Change 阈值
  - `--p-cutoff`: P-value 阈值

### 2. 柱状图 (Bar Plot)

支持多种误差棒样式的柱状图，适用于展示实验分组数据的均值和差异。

- **命令**: `bar`
- **关键参数**:
    - `--error-bar-type`: 自动计算误差棒类型，支持 `SD` (标准差), `SE` (标准误), `CI` (默认 95% 置信区间)。
    - `--error-bar-ci`: 当类型为 `CI` 时的置信区间大小（默认 95）。
    - `--error-bar-max` / `--error-bar-min`: 指定包含自定义误差范围的列名。
    - `--error-bar-capsize`: 误差棒横线宽度 (默认: 0.1)。
    - `--significance`: 进行显著性检验的配对列表（例如 "Control,Treated"）。
    - `--test`: 统计检验方法（t-test_ind, t-test_welch, Mann-Whitney 等）。
    - `--text-format`: 显著性标记格式 (star, full, simple, pvalue)。

### 3. 热图 (Heatmap)

支持行列聚类的热图，常用于展示基因表达谱或样本相关性。

- **命令**: `heatmap`
- **关键参数**:
  - `--cluster-rows` / `--cluster-cols`: 是否开启行/列聚类。
  - `--z-score`: 行(0)或列(1)标准化。

### 4. 主成分分析图 (PCA Plot)

用于展示样本的降维聚类情况，支持自动分组着色和置信椭圆。

- **命令**: `pca`
- **关键参数**:
  - `--transpose / --no-transpose`: 是否转置输入数据（默认开启，假设输入为 基因 x 样本）。
  - `--hue`: 分组列名。
  - `--cluster`: 是否开启聚类/置信椭圆绘制。
  - `--n-clusters`: 自动 KMeans 聚类的簇数量（仅当未提供 hue 时生效）。

### 5. 折线图 (Line Plot)

用于展示时间序列数据或变化趋势。

- **命令**: `line`
- **关键参数**:
  - `--hue`: 分组变量列名。

## 🎨 自定义主题 (Custom Themes)

除了内置的 `nature`、`science` 和 `default` 主题外，您还可以加载自己的主题配置。

### 使用 JSON 文件

创建一个 JSON 文件（例如 `my_theme.json`），定义您的样式参数：

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

使用方法：

```bash
uv run bio-plot pca expression.csv --theme ./my_theme.json
```

### 使用 Python 文件

创建一个 Python 文件（例如 `my_theme.py`），定义一个 `PlotTheme` 实例：

```python
from bio_plot.theme import PlotTheme

THEME = PlotTheme(
    name="custom_py",
    style="whitegrid",
    context="poster",
    rc_params={
        "font.size": 16,
        "axes.titlesize": 20
    }
)
```

使用方法：

```bash
uv run bio-plot pca expression.csv --theme ./my_theme.py
```

## 🚀 用法示例 (Usage)

### 绘制火山图

```bash
# 读取 CSV 文件并输出为 PNG
uv run bio-plot volcano result.csv -o volcano.png --fc-cutoff 1.5 --p-cutoff 0.01 --title "Volcano Plot ($p < 0.01$)"
```

### 绘制 PCA 图（带置信椭圆）

```bash
# 读取表达矩阵，按 Group 分组并绘制椭圆
uv run bio-plot pca expression.csv --hue Group --cluster -o pca.png
```

### 绘制带误差棒的柱状图 (使用 SE)

```bash
# 读取 Excel 文件，按 Group 分组
uv run bio-plot bar data.xlsx -x Treatment -y Value --hue Group --error-bar-type SE -o bar_plot.pdf
```

### 绘制带误差棒的柱状图 (使用 99% CI)
```bash
# 读取 Excel 文件，按 Group 分组
uv run bio-plot bar data.xlsx -x Treatment -y Value --hue Group --error-bar-type CI --error-bar-ci 99 -o bar_plot_ci.pdf
```

### 绘制带显著性标记的柱状图
```bash
# 比较 Control 和 Treated 组
uv run bio-plot bar data.csv -x Group -y Value --significance "Control,Treated" --test t-test_ind -o bar_sig.png
```

### 绘制聚类热图

```bash
# 对行进行 Z-score 标准化并聚类
uv run bio-plot heatmap expression.tsv --index-col GeneID --z-score 0 -o heatmap.png
```

## 🛠️ 开发 (Development)

```bash
# 运行单元测试
uv run pytest packages/plot/tests
```
