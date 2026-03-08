# bio-analyze-rna-seq

**bio-analyze-rna-seq** 是 `bio-analyze` 工具箱中的转录组分析专用模块。它提供了一套从原始测序数据到最终可视化报告的自动化全流程解决方案。

## ✨ 核心特性 (Features)

- **全自动工作流**：一键完成从 FastQ 到 HTML 报告的所有步骤。
- **质量控制 (QC)**：使用 `FastQC` 生成专业质控报告，并集成 `fastp` 进行高效的数据修剪和过滤。
- **极速定量**：使用 `Salmon` 进行基于伪比对（Pseudo-alignment）的转录本定量，速度极快且准确。
- **差异表达分析**：基于 Python 原生实现的 `PyDESeq2`，提供稳健的差异基因筛选。
- **富集分析**：使用 `GSEApy` 自动进行 GO (Gene Ontology) 和 KEGG 通路富集分析。
- **可视化报告**：生成交互式 HTML 报告，包含 PCA 图、火山图、热图及详细的数据统计表。
- **自动参考基因组**：只需指定物种名称（如 "Homo sapiens"），即可自动下载并构建索引。

## 🚀 快速开始 (Usage)

### 1. 准备数据

将所有的 FastQ 文件（`.fastq.gz` 或 `.fq.gz`）放入一个文件夹中。支持双端（`_R1`/`_R2` 或 `_1`/`_2`）和单端测序数据。

### 2. 准备实验设计文件 (Design File)

创建一个 CSV 文件（例如 `design.csv`），定义样本与实验条件的关系。必须包含 `sample` 和 `condition` 两列：

| sample  | condition |
| :------ | :-------- |
| sample1 | control   |
| sample2 | control   |
| sample3 | treated   |
| sample4 | treated   |

> **注意**：`sample` 列的名称必须与 FastQ 文件名对应（不含后缀和 `_R1`/`_R2` 部分）。

### 3. 运行分析

使用以下命令启动分析流程：

```bash
uv run bioanalyse rna_seq run \
    --input ./raw_data \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens" \
    --threads 8
```

### 4. 参数详解

- `-i, --input <DIR>`: **(必选)** 包含原始 FastQ 文件的目录路径。
- `-o, --output <DIR>`: **(必选)** 分析结果输出目录。
- `-d, --design <FILE>`: **(必选)** 实验设计 CSV 文件路径。
- `-s, --species <STR>`: **(可选)** 物种名称（例如 "Homo sapiens", "Mus musculus"）。用于自动下载参考基因组和富集分析。
- `--genome-fasta <FILE>`: **(可选)** 本地参考基因组 FASTA 文件路径（覆盖 `--species`）。
- `--genome-gtf <FILE>`: **(可选)** 本地基因组注释 GTF 文件路径（覆盖 `--species`）。
- `-t, --threads <INT>`: **(可选)** 并行线程数 (默认: 4)。
- `--skip-qc`: 跳过质量控制步骤。
- `--skip-trim`: 跳过修剪步骤（仅做 QC）。

## 📊 输出结果 (Outputs)

分析完成后，`--output` 目录将包含以下结构：

```
analysis_results/
├── reference/          # 下载或整理的参考基因组文件
├── qc/                 # fastp 生成的清洗后数据及 QC 报告 (.html/.json)
├── quant/              # Salmon 定量结果 (counts.csv 为合并后的表达矩阵)
├── de/                 # 差异表达分析结果 (deseq2_results.csv)
├── enrichment/         # GO/KEGG 富集分析结果表
├── report/             # 最终汇总报告
│   └── report.html     # <--- 请在浏览器中打开此文件查看完整报告
└── logs/               # 运行日志
```

## ⚙️ 环境要求 (Requirements)

本模块依赖以下外部工具，请确保它们已安装并在系统 PATH 中可用：

1. **fastp**: (必须) 用于数据修剪和基本 QC。
2. **salmon**: (必须) 用于定量。
3. **fastqc**: (可选) 用于生成详细质量控制报告。如果未安装，将仅使用 fastp 进行 QC。
4. **gffread**: (可选) 如果提供基因组 FASTA+GTF 但没有转录本 FASTA，用于提取转录本序列。

可以通过 `conda` 或 `mamba` 快速安装这些依赖：

```bash
conda install -c bioconda fastp salmon fastqc gffread
```
