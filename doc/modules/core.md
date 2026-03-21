# bio-analyze-core

The `bio-analyze-core` module provides the infrastructure for the entire toolkit. Although primarily used internally by other modules, it also provides some user-configurable global options.

## Log Configuration

You can control the log detail level of the tool via environment variables or configuration files.

### Log Levels

Supported levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

Default level is `INFO`.

### Configuration Methods

Usually can be set via specific tool CLI parameters, or by setting the `BIO_ANALYZE_LOG_LEVEL` environment variable (if supported by the specific tool wrapper).

## Sequence Processing (`sequence`)

The `bio_analyze_core.sequence` submodule provides a comprehensive set of functions for processing biological sequences (DNA/RNA/Protein). It acts as a lightweight alternative to larger bioinformatics libraries, using Python standard library implementations with optional `Biopython` acceleration when available.

### Features

- **Validation**: Check if sequences are valid DNA, RNA, or Protein (supports strict mode and IUPAC ambiguous bases).
- **Format Parsing**: Read and write FASTA and FASTQ files efficiently using Python generators.
- **Basic Manipulations**: Calculate reverse complements, standard complements, and GC content.
- **Translation & Transcription**: Transcribe DNA to RNA, reverse transcribe, and translate nucleic acids to proteins using standard codon tables.
- **Search & Alignment**:
  - `search_sequence`: Find sub-sequences supporting exact matches and IUPAC ambiguity.
  - `run_blast`: Perform sequence alignments. Supports **online NCBI BLAST** (via Biopython) and a **custom local Smith-Waterman algorithm** against local FASTA databases (no external CLI tools required).

### Example Usage

```python
from bio_analyze_core.sequence import (
    is_valid_dna,
    reverse_complement,
    read_fasta,
    run_blast
)

# 1. Validation and Manipulation
if is_valid_dna("ATGCGT"):
    rev_comp = reverse_complement("ATGCGT")
    print(f"Reverse complement: {rev_comp}")

# 2. Reading FASTA files efficiently
for header, seq in read_fasta("genome.fasta"):
    print(f"Read {header} with length {len(seq)}")

# 3. Local BLAST (Internal Smith-Waterman Engine)
# No need to install external blast+ tools
blast_results = run_blast(
    query_sequence={"my_query": "ATGCGTATGC"},
    local=True,
    local_db_path="local_database.fasta",
    evalue=10.0
)
print(blast_results["my_query"])
```
