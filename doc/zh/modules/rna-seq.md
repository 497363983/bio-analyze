# bio-analyze-rna-seq

**bio-analyze-rna-seq** 是 `bio-analyze` 工具箱中的转录组分析专用模块。它提供了一套从原始测序数据到最终可视化报告的自动化全流程解决方案。

## ✨ 核心特性 (Features)

- **全自动工作流**：一键完成从 FastQ 到 HTML 报告的所有步骤。
- **配置灵活**：支持命令行参数，也支持通过 JSON/YAML 配置文件管理参数。
- **模块化执行**：支持单独运行分析流程中的特定步骤（如仅运行 QC 或定量）。
- **SRA 自动下载**：支持直接输入 NCBI SRA Accession ID，自动下载数据并转换为 FASTQ 格式。
- **质量控制 (QC)**：使用 `FastQC` 生成专业质控报告，并集成 `fastp` 进行高效的数据修剪和过滤。
- **极速定量**：使用 `Salmon` 进行基于伪比对（Pseudo-alignment）的转录本定量，速度极快且准确。
- **差异表达分析**：基于 Python 原生实现的 `PyDESeq2`，提供稳健的差异基因筛选。
- **富集分析**：使用 `GSEApy` 自动进行 GO (Gene Ontology) 和 KEGG 通路富集分析，以及 GSEA (Gene Set Enrichment Analysis)。
- **可视化报告**：生成交互式 HTML 报告，包含 PCA 图、火山图、热图、富集分析结果及 GSEA 富集图。
- **自动参考基因组**：只需指定物种名称（如 "Homo sapiens"），即可自动下载并构建索引。

## 🚀 快速开始 (Usage)

### 场景 1：使用本地数据

#### 1. 准备数据

将所有的 FastQ 文件（`.fastq.gz` 或 `.fq.gz`）放入一个文件夹中。支持双端（`_R1`/`_R2` 或 `_1`/`_2`）和单端测序数据。

#### 2. 准备实验设计文件 (Design File)

创建一个 CSV 文件（例如 `design.csv`），定义样本与实验条件的关系。必须包含 `sample` 和 `condition` 两列：

| sample  | condition |
| :------ | :-------- |
| sample1 | control   |
| sample2 | control   |
| sample3 | treated   |
| sample4 | treated   |

> **注意**：`sample` 列的名称必须与 FastQ 文件名对应（不含后缀和 `_R1`/`_R2` 部分）。

#### 3. 运行分析

使用以下命令启动分析流程：

```bash
uv run bioanalyze rna_seq run \
    --input ./raw_data \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens" \
    --threads 8
```

### 场景 2：直接使用 SRA ID

如果您没有本地数据，可以直接提供 NCBI SRA Accession ID，工具会自动下载、转换并运行分析。

```bash
uv run bioanalyze rna_seq run \
    --sra-id SRR12345678 \
    --sra-id SRR12345679 \
    --output ./analysis_results \
    --design ./design.csv \
    --species "Homo sapiens"
```

> **注意**：下载的数据将保存在 `--output` 指定目录下的 `raw_data` 子目录中。

### 场景 3：使用配置文件 (JSON/YAML)

为了简化长命令行，您可以将参数写入配置文件（如 `config.yaml`）：

```yaml
input_dir: "./raw_data"
output_dir: "./analysis_results"
design_file: "./design.csv"
species: "Homo sapiens"
threads: 8
skip_qc: false

# 高级 QC 配置 (可选)
qc:
  qualified_quality_phred: 20
  length_required: 30
  dedup: true
```

然后运行：

```bash
uv run bioanalyze rna_seq run --config config.yaml
```

### 场景 4：分步执行 (Step-by-Step)

您可以使用独立的子命令来运行分析流程中的特定步骤，这提供了更大的灵活性。

#### 1. 下载数据 (download)
```bash
uv run bioanalyze rna_seq download --sra-id SRR123456 -o ./raw_data
```

#### 2. 准备参考基因组 (genome)
```bash
uv run bioanalyze rna_seq genome -s "Homo sapiens" -o ./reference
# 或者指定本地文件
uv run bioanalyze rna_seq genome --fasta genome.fa --gtf genes.gtf -o ./reference
```

#### 3. 质量控制 (qc)
```bash
uv run bioanalyze rna_seq qc -i ./raw_data -o ./qc_results
```

#### 4. 比对 (align) - 可选
```bash
uv run bioanalyze rna_seq align -i ./qc_results -o ./align_results --fasta ./reference/genome.fa --gtf ./reference/genes.gtf
```

#### 5. 定量 (quant)
```bash
uv run bioanalyze rna_seq quant -i ./qc_results -o ./quant_results --fasta ./reference/transcripts.fa
```

#### 6. 差异表达分析 (de)
```bash
uv run bioanalyze rna_seq de --counts ./quant_results/counts.csv --design design.csv -o ./de_results
```

#### 7. 富集分析 (enrich)
```bash
uv run bioanalyze rna_seq enrich --de-results ./de_results/deseq2_results.csv -s "Homo sapiens" -o ./enrich_results
```

## 📋 命令详解 (Commands)

### `run` (全流程)
运行完整的 RNA-Seq 分析流程。

### `download`
从 NCBI SRA 下载数据并转换为 FastQ 格式。
- `--sra-id`: SRA Accession ID。
- `-o, --output`: 输出目录。

### `genome`
准备参考基因组（下载或索引）。
- `-s, --species`: 物种名称。
- `--fasta`: 本地 FASTA 文件。
- `--gtf`: 本地 GTF 文件。

### `qc`
运行质控和修剪。
- `-i, --input`: 输入目录。
- `-o, --output`: 输出目录。
- `--skip-trim`: 跳过修剪。

### `align`
运行 STAR 比对。
- `-i, --input`: Clean reads 目录。
- `--fasta`: 基因组 FASTA。
- `--gtf`: 基因组 GTF。

### `quant`
运行 Salmon 定量。
- `-i, --input`: Clean reads 目录。
- `--fasta`: 转录本/基因组 FASTA。

### `de`
运行 DESeq2 差异表达分析。
- `--counts`: 计数矩阵 CSV。
- `--design`: 设计矩阵 CSV。

### `enrich`
运行 GO/KEGG 富集分析。
- `--de-results`: DESeq2 结果 CSV。
- `-s, --species`: 物种名称。

### `gsea`
运行 GSEA 富集分析。
- `--de-results`: DESeq2 结果 CSV。
- `-s, --species`: 物种名称。
- `--gene-sets`: 基因集库名称（默认: KEGG_2021_Human）。
- `--ranking-metric`: 排序指标（默认: auto）。

## 📋 run 命令参数详解

- `-c, --config <FILE>`: **(可选)** JSON/YAML 配置文件路径。如果提供，文件中的参数将作为默认值。
- `--step <STR>`: **(可选)** 仅运行特定步骤 (`download`, `reference`, `qc`, `quant`, `de`, `enrichment`, `report`)。默认运行所有步骤。
- `-i, --input <DIR>`: **(可选)** 包含原始 FastQ 文件的目录路径。如果未提供 `--sra-id`，则此参数为必选。
- `--sra-id <STR>`: **(可选)** NCBI SRA Accession ID (例如 `SRR123456`)。可以多次使用以指定多个 ID。
- `-o, --output <DIR>`: **(必选)** 分析结果输出目录。
- `-d, --design <FILE>`: **(必选)** 实验设计 CSV 文件路径。
- `-s, --species <STR>`: **(可选)** 物种名称（例如 "Homo sapiens", "Mus musculus"）。用于自动下载参考基因组和富集分析。
- `--genome-fasta <FILE>`: **(可选)** 本地参考基因组 FASTA 文件路径（覆盖 `--species`）。
- `--genome-gtf <FILE>`: **(可选)** 本地基因组注释 GTF 文件路径（覆盖 `--species`）。
- `-t, --threads <INT>`: **(可选)** 并行线程数 (默认: 4)。
- `--skip-qc`: 跳过质量控制步骤。
- `--skip-trim`: 跳过修剪步骤（仅做 QC）。
- `--star-align`: 启用 STAR 比对并生成染色体分布图。
- `--theme <STR>`: 指定绘图主题 (默认: `default`, 可选: `nature`, `science` 等)。

### 🔧 高级质控参数 (QC Options)

这些参数将直接传递给 `fastp` 用于数据清洗：

- `--qualified-quality-phred <INT>`: 碱基质量值阈值 (Phred)。默认 15 (Q15)。
- `--unqualified-percent-limit <INT>`: 允许的低质量碱基百分比限制 (0-100)。默认 40 (40%)。
- `--n-base-limit <INT>`: 允许的 N 碱基数量限制。默认 5。
- `--length-required <INT>`: 长度过滤阈值，短于此长度的 reads 将被丢弃。默认 15。
- `--max-len1 <INT>`: Read1 的最大长度限制，超过部分将被修剪。默认 0 (不限制)。
- `--max-len2 <INT>`: Read2 的最大长度限制，超过部分将被修剪。默认 0 (不限制)。
- `--adapter-sequence <STR>`: Read1 的接头序列。未提供则自动检测。
- `--adapter-sequence-r2 <STR>`: Read2 的接头序列。未提供则自动检测。
- `--trim-front1 <INT>`: Read1 5' 端修剪碱基数。
- `--trim-tail1 <INT>`: Read1 3' 端修剪碱基数。
- `--cut-right`: 启用滑动窗口从 3' 端修剪 (cut_right)。
- `--cut-window-size <INT>`: cut_right 的窗口大小。默认 4。
- `--cut-mean-quality <INT>`: cut_right 的平均质量阈值。默认 20。
- `--dedup`: 启用去重 (deduplication)。
- `--poly-g-min-len <INT>`: polyG 尾修剪的最小长度检测阈值。默认 10。

## 📦 Python API

### 1. 全流程 (`RNASeqPipeline`)

```python
from bio_analyze_rna_seq import RNASeqPipeline
from pathlib import Path

pipeline = RNASeqPipeline(
    input_dir=Path("./raw_data"),
    output_dir=Path("./results"),
    design_file=Path("design.csv"),
    species="Homo sapiens",
    threads=8,
    skip_qc=False
)

pipeline.run()
```

### 2. SRA 下载 (`SRAManager`)

```python
from bio_analyze_rna_seq.sra import SRAManager
from pathlib import Path

manager = SRAManager(output_dir=Path("./raw_data"), threads=4)
manager.download(["SRR123456", "SRR789012"])
```

### 3. 定量 (`QuantManager`)

```python
from bio_analyze_rna_seq.quant import QuantManager
from pathlib import Path

reads = {
    "sample1": {"R1": "sample1_1.fq.gz", "R2": "sample1_2.fq.gz"}
}
reference = {
    "fasta": Path("genome.fa"),
    "gtf": Path("genes.gtf")
}

manager = QuantManager(
    reads=reads,
    reference=reference,
    output_dir=Path("./quant_results"),
    threads=8
)

# 返回合并后的计数矩阵 (DataFrame)
counts_df = manager.run()
```

### 4. 报告生成 (`ReportGenerator`)

```python
from bio_analyze_rna_seq.report import ReportGenerator
from pathlib import Path

# 需要传入前面步骤的结果
generator = ReportGenerator(
    output_dir=Path("./report"),
    qc_stats=qc_data,          # from QCNode
    counts=counts_df,          # from QuantNode
    de_results=de_df,          # from DENode
    enrich_results=enrich_dict # from EnrichmentNode
)

generator.generate()
```

## ⚙️ 环境要求 (Requirements)

本模块依赖以下外部工具，请确保它们已安装并在系统 PATH 中可用：

1. **fastp**: (必须) 用于数据修剪和基本 QC。
2. **salmon**: (必须) 用于定量。
3. **fastqc**: (可选) 用于生成详细质量控制报告。如果未安装，将仅使用 fastp 进行 QC。
4. **STAR**: (可选) 如果启用 `--star-align`，用于比对和染色体分布分析。
5. **samtools**: (可选) 如果启用 `--star-align`，用于 BAM 文件索引和统计。
6. **gffread**: (可选) 如果提供基因组 FASTA+GTF 但没有转录本 FASTA，用于提取转录本序列。
7. **sra-tools**: (可选) 如果使用 `--sra-id` 功能，必须安装 (包含 `prefetch` 和 `fasterq-dump`)。
