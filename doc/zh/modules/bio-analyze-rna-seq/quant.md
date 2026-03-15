---
---

# quant

使用 Salmon 进行转录本表达量定量。

## 命令行用法

**命令**: `quant`

### 关键参数

<ParamTable params-path="rna_seq/quant_cli" />

### 示例

```bash
uv run bioanalyze rna-seq quant -i ./clean_data -o ./quant_results --fasta transcripts.fa
```

## Python API

### `QuantManager`

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
