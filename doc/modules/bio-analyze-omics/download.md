---
---

# download

Download FASTQ files from SRA.

## CLI Usage

**Command**: `download`

### Arguments

<ParamTable params-path="omics/rna_seq_download_cli" />

### Example

```bash
uv run bioanalyze omics rna_seq download --sra-id SRR123456 -o ./raw_data
```

## Python API

### `SRAManager`

```python
from bio_analyze_omics.rna_seq.download import SRAManager

downloader = SRAManager(output_dir="./raw_data")
downloader.download(["SRR123456", "SRR123457"])
```
