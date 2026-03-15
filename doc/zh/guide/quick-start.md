---
order: 3
---

# 快速开始

本指南将帮助您快速上手 `bio-analyze` 并完成常见的生物信息学任务。

## 1. 验证安装

首先，确保 `bio-analyze` 已正确安装：

```bash
bio-analyze --version
```

## 2. 基础用法

### 绘制火山图

可视化差异表达结果是最常见的任务之一。

1. **准备数据**: 包含 `log2FoldChange` 和 `padj` (或 p-value) 列的 CSV 文件。
2. **运行命令**:

```bash
bio-analyze plot volcano results.csv --fc-cutoff 1.5 --p-cutoff 0.05
```

这将在当前目录生成 `volcano.png` (或 PDF)。

### 运行 RNA-Seq 流程

运行完整的 RNA-Seq 分析流程（从原始 Reads 到表达矩阵）：

```bash
# 初始化新项目配置
bio-analyze rna-seq init my_project

# 编辑 config.yaml 指定您的 FASTQ 文件和参考基因组

# 运行流程
bio-analyze rna-seq run --config my_project/config.yaml
```

## 3. 获取帮助

您随时可以使用 `--help` 参数查看任何模块的可用命令和选项：

```bash
# 列出所有模块
bio-analyze --help

# 获取特定模块的帮助 (如 plot)
bio-analyze plot --help

# 获取特定图表类型的帮助
bio-analyze plot volcano --help
```

## 下一步

- 探索 **功能模块** 部分，了解特定工具（绘图、RNA-Seq 等）。
- 查看 **示例** 以了解更复杂的用例。
