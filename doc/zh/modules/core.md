# bio-analyze-core

`bio-analyze-core` 模块为整个工具箱提供了基础设施。虽然主要供其他模块内部调用，但也提供了一些用户可配置的全局选项。

## 日志配置

您可以通过环境变量或配置文件控制工具的日志详细程度。

### 日志级别

支持的级别：`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`。

默认级别为 `INFO`。

### 配置方式

通常可以通过具体工具的 CLI 参数设置，或者设置 `BIO_ANALYZE_LOG_LEVEL` 环境变量（如果具体工具封装支持）。

## 生物序列处理 (`sequence` 子模块)

`bio_analyze_core.sequence` 子模块提供了一套全面的生物序列（DNA/RNA/蛋白质）处理功能。它作为大型生物信息学库的轻量级替代方案，优先使用 Python 标准库实现，并在环境存在时自动调用 `Biopython` 进行加速。

### 核心特性

- **序列验证**: 检查序列是否为合法的 DNA、RNA 或蛋白质（支持严格模式和 IUPAC 模糊碱基）。
- **格式解析**: 使用 Python 生成器高效读取和写入 FASTA 和 FASTQ 文件，支持大文件处理。
- **基础操作**: 计算反向互补序列、标准互补序列以及 GC 含量。
- **转录与翻译**: 提供 DNA 转录 RNA、逆转录，以及基于标准密码子表将核酸翻译为蛋白质的功能。
- **搜索与比对**:
  - `search_sequence`: 查找子序列，支持精确匹配和基于 IUPAC 规则的模糊匹配。
  - `run_blast`: 序列比对。支持 **在线 NCBI BLAST**（通过 Biopython）和基于 **自定义 Smith-Waterman 算法** 的本地 FASTA 数据库比对（无需依赖外部的 blast+ 命令行工具）。

### 使用示例

```python
from bio_analyze_core.sequence import (
    is_valid_dna,
    reverse_complement,
    read_fasta,
    run_blast
)

# 1. 验证和基础操作
if is_valid_dna("ATGCGT"):
    rev_comp = reverse_complement("ATGCGT")
    print(f"反向互补序列: {rev_comp}")

# 2. 高效读取 FASTA 文件
for header, seq in read_fasta("genome.fasta"):
    print(f"读取到序列 {header}，长度为 {len(seq)}")

# 3. 本地 BLAST (内部 Smith-Waterman 引擎)
# 无需安装外部的 blast+ 工具
blast_results = run_blast(
    query_sequence={"my_query": "ATGCGTATGC"},
    local=True,
    local_db_path="local_database.fasta",
    evalue=10.0
)
print(blast_results["my_query"])
```
