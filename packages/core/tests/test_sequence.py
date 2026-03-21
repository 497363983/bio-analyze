from io import StringIO

import pytest

from bio_analyze_core.sequence import (
    complement,
    gc_content,
    is_valid_dna,
    is_valid_protein,
    is_valid_rna,
    read_fasta,
    read_fastq,
    reverse_complement,
    reverse_transcribe,
    run_blast,
    search_sequence,
    transcribe,
    translate,
    write_fasta,
    write_fastq,
)


def test_validation():
    # DNA
    assert is_valid_dna("ATCG")
    assert is_valid_dna("atcg")
    assert is_valid_dna("ATCGN", strict=False)
    assert not is_valid_dna("ATCGN", strict=True)
    assert not is_valid_dna("ATXG")

    # RNA
    assert is_valid_rna("AUCG")
    assert is_valid_rna("aucg")
    assert is_valid_rna("AUCGN", strict=False)
    assert not is_valid_rna("AUCGN", strict=True)
    assert not is_valid_rna("ATCG", strict=True) # T is invalid in strict RNA

    # Protein
    assert is_valid_protein("MKVLY")
    assert is_valid_protein("mkvly")
    assert is_valid_protein("M*")
    assert not is_valid_protein("MK123")


def test_fasta(tmp_path):
    fasta_content = ">seq1\nATCG\n>seq2\nGCTA\n"
    f = StringIO(fasta_content)
    records = list(read_fasta(f))
    assert len(records) == 2
    assert records[0] == ("seq1", "ATCG")
    assert records[1] == ("seq2", "GCTA")

    # Write test
    out_file = tmp_path / "test.fasta"
    write_fasta(records, out_file)
    read_back = list(read_fasta(out_file))
    assert read_back == records


def test_fastq(tmp_path):
    fastq_content = "@seq1\nATCG\n+\n!!!!\n@seq2\nGCTA\n+\n????\n"
    f = StringIO(fastq_content)
    records = list(read_fastq(f))
    assert len(records) == 2
    assert records[0] == ("seq1", "ATCG", "", "!!!!")
    assert records[1] == ("seq2", "GCTA", "", "????")

    # Write test
    out_file = tmp_path / "test.fastq"
    write_fastq(records, out_file)
    read_back = list(read_fastq(out_file))
    assert read_back == records

    # Invalid FASTQ
    bad_content = "@seq1\nATCG\n+\n!!!\n" # length mismatch
    with pytest.raises(ValueError):
        list(read_fastq(StringIO(bad_content)))


def test_reverse_complement():
    assert reverse_complement("ATCG") == "CGAT"
    assert reverse_complement("atcg") == "cgat"
    assert complement("ATCG") == "TAGC"

    # RNA
    assert reverse_complement("AUCG", is_rna=True) == "CGAU"
    assert complement("AUCG", is_rna=True) == "UAGC"


def test_gc_content():
    assert gc_content("GCGC") == 1.0
    assert gc_content("ATAT") == 0.0
    assert gc_content("ATGC") == 0.5
    # Ignore N
    assert gc_content("ATGCN") == 0.5


def test_transcription():
    assert transcribe("ATCG") == "AUCG"
    assert transcribe("atcg") == "aucg"

    assert reverse_transcribe("AUCG") == "ATCG"
    assert reverse_transcribe("aucg") == "atcg"


def test_translation():
    # ATG -> M, TAA -> *
    assert translate("ATGTAA") == "M*"
    assert translate("ATGTAA", to_stop=True) == "M"

    # RNA translation
    assert translate("AUGUAA", is_rna=True) == "M*"


def test_search_sequence():
    target = "ATGCGTATGC"
    # exact
    assert search_sequence("ATGC", target) == [(0, 4), (6, 10)]
    assert search_sequence("CGT", target) == [(3, 6)]

    # ambiguous
    assert search_sequence("N", "AT", allow_ambiguous=True) == [(0, 1), (1, 2)]
    assert search_sequence("R", "AGCT", allow_ambiguous=True) == [(0, 1), (1, 2)] # A and G


def test_blast_local_not_found():
    # 测试在本地模式下找不到数据库文件的情况
    with pytest.raises(FileNotFoundError):
        run_blast("ATCG", program="blastn", local=True, database="fake_db.fasta")

def test_blast_empty_query():
    assert run_blast("") == {}
    assert run_blast([]) == {}
    assert run_blast({}) == {}

def test_blast_local_internal(tmp_path):
    # 创建临时的 FASTA 数据库
    db_file = tmp_path / "db.fasta"
    with open(db_file, "w", encoding="utf-8") as f:
        f.write(">seq1\nATGCGTATGC\n")
        f.write(">seq2\nCGTACGTA\n")

    # 单序列查询
    res1 = run_blast("ATGC", program="blastn", local=True, local_db_path=db_file, evalue=100.0)
    assert "query" in res1
    assert len(res1["query"]) > 0
    # ATGC 应该匹配 seq1
    assert any(hit["hit_id"] == "seq1" for hit in res1["query"])

    # 多序列查询
    res2 = run_blast({"q1": "ATGC", "q2": "CGTA"}, program="blastn", local=True, local_db_path=db_file, evalue=100.0)
    assert "q1" in res2
    assert "q2" in res2
    assert len(res2["q1"]) > 0
    assert len(res2["q2"]) > 0
