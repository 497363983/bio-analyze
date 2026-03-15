# bio-analyze-plot 绘图模块

**bio-analyze-plot** 是 `bio-analyze` 工具箱中的专业绘图模块。它基于 `matplotlib` 和 `seaborn` 构建，旨在生成各类生物信息学统计图表，并支持灵活的主题定制。

## ✨ 核心特性

- **可定制主题**：提供内置主题（Nature/Science）作为基础，同时支持完全自定义字体、字号、线条粗细和配色方案。
- **广泛的数据支持**：支持 `.csv`、`.tsv`、`.txt`、`.xlsx` 及 `.xls` 格式，可通过 `--sheet` 指定 Excel 工作表。
- **多格式导出**：支持 `png`、`pdf`、`svg`、`jpg`、`tiff` 等多种图像格式。
- **中文注释**：代码注释全中文，便于开发者阅读和二次开发。
- **LaTeX 支持**：自动解析坐标轴标签中的 LaTeX 公式（如 `$y = \sin(x)$`）。
- **统一 CLI**：所有图表均可通过统一的命令行接口调用。

## 🎨 主题定制 (Themes)

支持通过 JSON 文件或 Python 代码自定义绘图主题。

### 使用内置主题

```bash
# 使用 Nature 风格
bio-analyze plot volcano result.csv --theme nature

# 使用 Science 风格
bio-analyze plot volcano result.csv --theme science
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

使用: `bio-analyze plot volcano ... --theme ./my_theme.json`

## 💻 开发 (Development)

单元测试输出位于 `packages/plot/tests/output` 目录。

```bash
pytest packages/plot/tests
```
