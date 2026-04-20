import os
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TextIO


def read_fastq(file_path_or_obj: str | Path | TextIO) -> Iterator[tuple[str, str, str, str]]:
    """
    Read FASTQ format file or file object record by record, returning a generator.

    Args:
        file_path_or_obj:
            FASTQ file path or opened file object.

    Yields:
        tuple[str, str, str, str]:
            (Header, Sequence, Quality header, Quality string) tuple. Header does not include the "@" symbol.
    """
    if isinstance(file_path_or_obj, (str, Path, os.PathLike)):
        with open(file_path_or_obj, encoding="utf-8") as f:
            yield from _read_fastq_obj(f)
    else:
        yield from _read_fastq_obj(file_path_or_obj)

def _read_fastq_obj(f: TextIO) -> Iterator[tuple[str, str, str, str]]:
    while True:
        header_line = f.readline()
        if not header_line:
            break
        header_line = header_line.strip()
        if not header_line:
            continue

        if not header_line.startswith("@"):
            raise ValueError(f"FASTQ record must start with '@', got: {header_line}")

        seq_line = f.readline().strip()
        plus_line = f.readline().strip()
        qual_line = f.readline().strip()

        if not plus_line.startswith("+"):
            raise ValueError("FASTQ quality header must start with '+'")

        if len(seq_line) != len(qual_line):
            raise ValueError("FASTQ sequence and quality strings must have the same length")

        yield header_line[1:], seq_line, plus_line[1:], qual_line

def write_fastq(records: Iterable[tuple[str, str, str, str]], file_path_or_obj: str | Path | TextIO) -> None:
    """
    Write records to FASTQ format file or file object.

    Args:
        records:
            Iterable containing (Header, Sequence, Quality header, Quality string).
        file_path_or_obj:
            Target file path or opened file object.
    """
    if isinstance(file_path_or_obj, (str, Path, os.PathLike)):
        with open(file_path_or_obj, "w", encoding="utf-8") as f:
            _write_fastq_obj(records, f)
    else:
        _write_fastq_obj(records, file_path_or_obj)

def _write_fastq_obj(records: Iterable[tuple[str, str, str, str]], f: TextIO):
    for header, seq, qual_header, qual in records:
        if len(seq) != len(qual):
            raise ValueError(f"Sequence and quality lengths do not match for record {header}")
        f.write(f"@{header}\n")
        f.write(f"{seq}\n")
        f.write(f"+{qual_header}\n")
        f.write(f"{qual}\n")
