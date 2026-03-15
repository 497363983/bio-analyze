---
---

# run

运行完整的 RNA-Seq 分析流程。

## 命令行用法

**命令**: `run`

### 关键参数

<ParamTable params-path="rna_seq/run_cli" />

### 高级质控参数 (QC Options)

- `--fastqc-args <STR>`: 传递给 FastQC 的额外参数 (例如 `"--adapters adapter_list.txt"`)。
- `--multiqc-args <STR>`: 传递给 MultiQC 的额外参数。

### 示例

```bash
uv run bioanalyze rna-seq run -c config.json
```

## Python API

### `RNASeqPipeline`

```python
from bio_analyze_rna_seq.pipeline import RNASeqPipeline

pipeline = RNASeqPipeline(
    config_path="config.json",
    design_path="design.csv",
    output_dir="./results"
)

pipeline.run()
```

**RNASeqPipeline 参数:**

<ParamTable params-path="rna_seq/run_api" />
