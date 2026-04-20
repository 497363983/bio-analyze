import os
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TextIO


def read_fasta(file_path_or_obj: str | Path | TextIO) -> Iterator[tuple[str, str]]:
    """
    Read FASTA format file or file object record by record, returning a generator.

    Args:
        file_path_or_obj:
            FASTA file path or opened file object.

    Yields:
        tuple[str, str]:
            (Header, Sequence string) tuple. Header does not include the ">" symbol.
    """
    if isinstance(file_path_or_obj, (str, Path, os.PathLike)):
        with open(file_path_or_obj, encoding="utf-8") as f:
            yield from _read_fasta_obj(f)
    else:
        yield from _read_fasta_obj(file_path_or_obj)

def _read_fasta_obj(f: TextIO) -> Iterator[tuple[str, str]]:
    header = None
    seq_lines = []

    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                yield header, "".join(seq_lines)
            header = line[1:]
            seq_lines = []
        else:
            if header is None:
                raise ValueError("FASTA file does not start with '>'")
            seq_lines.append(line)

    if header is not None:
        yield header, "".join(seq_lines)

def write_fasta(
    records: Iterable[tuple[str, str]], file_path_or_obj: str | Path | TextIO, line_length: int = 80
) -> None:
    """
    Write records to FASTA format file or file object.

    Args:
        records:
            Iterable containing (Header, Sequence string) tuples.
        file_path_or_obj:
            Target file path or opened file object.
        line_length (int):
            Line length for sequence wrapping, default is 80. If 0 or negative, no wrapping.
    """
    if isinstance(file_path_or_obj, (str, Path, os.PathLike)):
        with open(file_path_or_obj, "w", encoding="utf-8") as f:
            _write_fasta_obj(records, f, line_length)
    else:
        _write_fasta_obj(records, file_path_or_obj, line_length)

def _write_fasta_obj(records: Iterable[tuple[str, str]], f: TextIO, line_length: int):
    for header, seq in records:
        f.write(f">{header}\n")
        if line_length > 0:
            for i in range(0, len(seq), line_length):
                f.write(f"{seq[i:i+line_length]}\n")
        else:
            f.write(f"{seq}\n")
