---
---

# run

运行完整的 RNA-Seq 分析流程。

## 命令行用法

**命令**: `run`

### 关键参数

<ParamTable params-path="omics/rna_seq_run_cli" />

### 高级质控参数 (QC Options)

- `--fastqc-args <STR>`: 传递给 FastQC 的额外参数 (例如 `"--adapters adapter_list.txt"`)。
- `--multiqc-args <STR>`: 传递给 MultiQC 的额外参数。

### 示例

```bash
uv run bioanalyze omics rna_seq run -c config.json
```

对于物种名不容易被 `genomepy` 识别的情况，可以直接提供组装号：

```bash
uv run bioanalyze omics rna_seq run \
  --input ./raw_data \
  --output ./results \
  --design ./design.csv \
  --assembly GCA_013347765.1
```

当提供 `--species` 时，CLI 会先调用 `genomepy.search()` 搜索候选基因组，展示结果后再提示你选择要下载的条目。

## Python API

### `RNASeqPipeline`

```python
from bio_analyze_omics.rna_seq.pipeline import RNASeqPipeline

pipeline = RNASeqPipeline(
    config_path="config.json",
    design_path="design.csv",
    output_dir="./results"
)

pipeline.run()
```

**RNASeqPipeline 参数:**

<ParamTable params-path="omics/run_api" />
