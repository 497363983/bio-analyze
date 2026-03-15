---
---

# download

从 SRA 数据库下载 FASTQ 文件。

## 命令行用法

**命令**: `download`

### 关键参数

<ParamTable params-path="rna_seq/download_cli" />

### 示例

```bash
uv run bioanalyze rna-seq download --sra-id SRR123456 -o ./raw_data
```

## Python API

### `SRAManager`

```python
from bio_analyze_rna_seq.download import SRAManager

downloader = SRAManager(output_dir="./raw_data")
downloader.download(["SRR123456", "SRR123457"])
```
