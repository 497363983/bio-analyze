"""
zh: 生物序列处理子模块。
en: Biological sequence processing submodule.

zh: 提供序列验证、格式解析(FASTA/FASTQ)、反向互补、GC含量、转录、翻译和搜索等基础功能。
en: Provides basic functions for sequence validation, format parsing (FASTA/FASTQ),
    reverse complement, GC content, transcription, translation, and searching.
"""

from .blast import run_blast
from .fasta import read_fasta, write_fasta
from .fastq import read_fastq, write_fastq
from .gc_content import gc_content
from .reverse_complement import complement, reverse_complement
from .search import search_sequence
from .transcribe import reverse_transcribe, transcribe
from .translate import translate
from .validate import is_valid_dna, is_valid_protein, is_valid_rna

__all__ = [
    "complement",
    "gc_content",
    "is_valid_dna",
    "is_valid_protein",
    "is_valid_rna",
    "read_fasta",
    "read_fastq",
    "reverse_complement",
    "reverse_transcribe",
    "run_blast",
    "search_sequence",
    "transcribe",
    "translate",
    "write_fasta",
    "write_fastq",
]
