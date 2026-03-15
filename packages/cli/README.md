# bio-analyze-cli

**bio-analyze-cli** 是 BioAnalyze 工具箱的统一命令行入口。它负责动态发现和加载各功能模块（如 `rna-seq`, `docking`, `plot` 等），并提供统一的 CLI 体验。

## 🚀 核心功能

- **插件式架构**：基于 `entry points` 机制，自动发现已安装的 `bio-analyze-*` 模块（例如 `bio-analyze-docking`, `bio-analyze-plot`）。
- **统一配置**：支持全局配置文件加载和日志管理。
- **脚手架工具**：内置 `create` 命令，快速生成新工具或绘图主题的模版。

## 🛠️ 常用命令

### 1. 基础命令

```bash
# 查看帮助
bioanalyze --help

# 查看已安装插件
bioanalyze plugins
```

### 2. 调用子模块

一旦安装了对应的功能模块包，即可通过 `bioanalyze` 直接调用：

```bash
# 运行 RNA-Seq 流程
bioanalyze rna_seq run --input ./data --output ./results

# 运行分子对接
bioanalyze docking run --receptor rec.pdb --ligand lig.sdf

# 运行绘图工具
bioanalyze plot volcano results.csv
```

### 3. 创建新项目/模版

使用 `create` 命令可以快速生成标准的项目结构。

**交互式创建：**

```bash
bioanalyze create
```

（随后根据提示选择类型和输入名称）

**快速创建新工具：**

```bash
bioanalyze create tool --name my-new-tool
```

这将在 `packages/my-new-tool` 下生成一个新的分析模块模版。

**快速创建绘图主题：**

```bash
bioanalyze create theme --name my-company-theme
```

这将在当前目录下生成一个名为 `my-company-theme` 的 Python 包，您可以修改其中的 `__init__.py` 来定制 `bio-plot` 的样式。

## 🔧 开发指南

### 添加新模块

1. 使用 `bioanalyze create tool` 创建模版。
2. 在 `pyproject.toml` 中配置 `[project.entry-points."bio_analyze.plugins"]`。
3. 实现 `get_app()` 函数返回 `typer.Typer` 实例。
4. 运行 `uv sync` 安装新模块。
5. 现在可以通过 `bioanalyze <tool-name>` 调用您的新工具了。
