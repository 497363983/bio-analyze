---
---

# bio-analyze-omics

当前提供 RNA-Seq 分析流程的组学模块。

## ✨ 核心特性

- **全自动工作流**：从原始数据质控、比对、定量到差异表达分析一键完成。
- **可复现性**：参数化配置管理，确保每次分析结果可追溯。
- **丰富报表**：自动生成 HTML 质控报告和交互式图表（火山图、热图、PCA、GSEA）。
- **工具集成**：内置最佳实践工具（FastQC, Trimmomatic, STAR/Salmon, DESeq2）。

## RNA-Seq 子命令

- [run](./run.md): 运行完整的 `bioanalyze omics rna_seq run` 流程。
- [download](./download.md): 从 SRA 下载 FASTQ 文件。
- [genome](./genome.md): 下载参考基因组。
- [qc](./qc.md): FASTQ 文件质量控制。
- [align](./align.md): 将 reads 比对到参考基因组。
- [quant](./quant.md): 转录本表达量定量。
- [de](./de.md): 差异表达分析。
- [enrich](./enrich.md): GO/KEGG 富集分析。
- [gsea](./gsea.md): GSEA 富集分析。

## ⚙️ 依赖工具 (Requirements)

该模块依赖以下外部工具，请确保它们已安装并在系统 PATH 中可用：

1. **fastp**: (必需) 用于数据修剪和基本质控。
2. **salmon**: (必需) 用于定量分析。
3. **fastqc**: (可选) 用于生成详细的质量控制报告。如果未安装，将仅使用 fastp 进行质控。
4. **STAR**: (可选) 如果启用了 `--star-align`，则用于比对和染色体分布分析。
5. **samtools**: (可选) 如果启用了 `--star-align`，则用于 BAM 文件索引和统计。
6. **gffread**: (可选) 如果提供了基因组 FASTA+GTF 但未提供转录本 FASTA，则用于提取转录本序列。
7. **sra-tools**: (可选) 如果使用 `--sra-id` 功能，则必须安装（包含 `prefetch` 和 `fasterq-dump`）。
