# bio-analyze-cli

**bio-analyze-cli** 是 BioAnalyze 工具箱的统一命令行入口。它负责动态发现和加载各功能模块（如 `rna-seq`, `docking`, `plot` 等），并提供统一的 CLI 体验。

## 🚀 核心功能

- **插件式架构**：基于 `entry points` 机制，自动发现已安装的 `bio-analyze-*` 模块（例如 `bio-analyze-docking`, `bio-analyze-plot`）。
- **统一配置**：支持全局配置文件加载和日志管理。

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
