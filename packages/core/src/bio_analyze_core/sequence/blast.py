import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:
    from Bio.Blast import NCBIWWW, NCBIXML
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

from .alignment import smith_waterman
from .fasta import read_fasta


def _parse_blast_xml(xml_content: str) -> dict[str, list[dict[str, Any]]]:
    """
    Simple parsing of BLAST XML results.
    """
    results: dict[str, list[dict[str, Any]]] = {}
    try:
        root = ET.fromstring(xml_content)
        for iteration in root.findall(".//Iteration"):
            query_id = iteration.findtext("Iteration_query-def", "query")
            if query_id not in results:
                results[query_id] = []

            for hit in iteration.findall(".//Hit"):
                hit_def = hit.findtext("Hit_def", "")
                hit_id = hit.findtext("Hit_id", "")
                for hsp in hit.findall(".//Hsp"):
                    evalue = hsp.findtext("Hsp_evalue", "")
                    identity = hsp.findtext("Hsp_identity", "")
                    align_len = hsp.findtext("Hsp_align-len", "")

                    results[query_id].append({
                        "hit_id": hit_id,
                        "hit_def": hit_def,
                        "evalue": float(evalue) if evalue else None,
                        "identity": int(identity) if identity else None,
                        "align_len": int(align_len) if align_len else None,
                    })
    except ET.ParseError:
        pass
    return results

def run_blast(
    query_sequence: str | list[str] | dict[str, str],
    program: str = "blastn",
    database: str = "nt",
    local: bool = False,
    local_db_path: str | Path | None = None,
    evalue: float = 10.0,
    **kwargs,
) -> dict[str, list[dict[str, Any]]]:
    """
    Run BLAST (supports online NCBI and local command line).

    Args:
        query_sequence (Union[str, list[str], dict[str, str]]):
            The query sequence to search. Can be a single string, a list of strings, or a dict of {name: sequence}.
        program (str):
            BLAST program name (e.g., 'blastn', 'blastp', 'blastx').
        database (str):
            Target database name.
        local (bool):
            Whether to use local BLAST+ tools. If True, corresponding BLAST program must be installed.
        local_db_path (Optional[Union[str, Path]]):
            Specific path to the local database FASTA file.
        evalue (float):
            E-value threshold.
        **kwargs:
            Additional arguments passed to NCBIWWW.qblast or local command line tool.

    Returns:
        dict[str, list[dict[str, Any]]]:
            Dictionary containing match results, keyed by query name, valued by list of match results.
    """
    if not query_sequence:
        return {}

    # 统一处理 query_sequence 为字典格式
    query_dict: dict[str, str] = {}
    if isinstance(query_sequence, str):
        query_dict = {"query": query_sequence}
    elif isinstance(query_sequence, list):
        for i, seq in enumerate(query_sequence):
            query_dict[f"query_{i+1}"] = seq
    elif isinstance(query_sequence, dict):
        query_dict = query_sequence
    else:
        raise ValueError("query_sequence must be a string, list of strings, or dict of strings.")

    if not query_dict:
        return {}

    if local:
        return _run_local_blast(query_dict, program, database, local_db_path, evalue, **kwargs)
    else:
        return _run_online_blast(query_dict, program, database, evalue, **kwargs)

def _run_online_blast(
    query_dict: dict[str, str], program: str, database: str, evalue: float, **kwargs
) -> dict[str, list[dict[str, Any]]]:
    if not HAS_BIOPYTHON:
        raise ImportError("Biopython is required for online BLAST. Please install biopython.")

    # 组装 FASTA 格式的查询字符串
    fasta_query = ""
    for name, seq in query_dict.items():
        fasta_query += f">{name}\n{seq}\n"

    # 调用 NCBIWWW.qblast
    result_handle = NCBIWWW.qblast(
        program,
        database,
        fasta_query,
        expect=evalue,
        **kwargs,
    )

    # 解析结果
    results: dict[str, list[dict[str, Any]]] = {}
    blast_records = NCBIXML.parse(result_handle)
    for record in blast_records:
        query_id = record.query
        # NCBI 返回的 query_id 可能会被截断或改变，尝试匹配原始字典
        if query_id not in results:
            results[query_id] = []

        for alignment in record.alignments:
            for hsp in alignment.hsps:
                results[query_id].append({
                    "hit_id": alignment.hit_id,
                    "hit_def": alignment.hit_def,
                    "evalue": hsp.expect,
                    "identity": hsp.identities,
                    "align_len": hsp.align_length,
                })

    result_handle.close()
    return results

def _calculate_evalue(score: int, m: int, n: int) -> float:
    """
    Extremely simple E-value estimation (for mock only, not standard BLAST statistical model)
    """
    # 假设 K 和 Lambda 为常数
    k = 0.1
    lambda_ = 0.3
    # E = K * m * n * e^(-Lambda * S)
    try:
        e_val = k * m * n * math.exp(-lambda_ * score)
        return e_val
    except OverflowError:
        return float('inf')

def _run_local_blast(
    query_dict: dict[str, str],
    program: str,
    database: str,
    local_db_path: str | Path | None,
    evalue: float,
    **kwargs,
) -> dict[str, list[dict[str, Any]]]:
    """
    Perform local alignment using internally implemented Smith-Waterman algorithm.
    """
    db_path = str(local_db_path) if local_db_path else database
    db_file = Path(db_path)

    if not db_file.exists() or not db_file.is_file():
        raise FileNotFoundError(f"Local database file not found: {db_file}. Please provide a valid FASTA file.")

    results: dict[str, list[dict[str, Any]]] = {q_id: [] for q_id in query_dict}

    # 逐条读取本地数据库 FASTA，与每个 query 进行比对
    for subject_id, subject_seq in read_fasta(db_file):
        n = len(subject_seq)
        for query_id, query_seq in query_dict.items():
            m = len(query_seq)

            # 执行 Smith-Waterman 比对
            score, _, _, identity, align_len = smith_waterman(
                query_seq,
                subject_seq,
                match_score=2,
                mismatch_penalty=-1,
                gap_penalty=-2
            )

            if score > 0:
                # 估算 evalue
                e_val = _calculate_evalue(score, m, n)

                # 根据阈值过滤
                if e_val <= evalue:
                    results[query_id].append({
                        "hit_id": subject_id,
                        "hit_def": f"Local match against {subject_id}",
                        "evalue": e_val,
                        "identity": identity,
                        "align_len": align_len,
                        "score": score,
                    })

    # 按 evalue 从小到大排序结果
    for q_id in results:
        results[q_id].sort(key=lambda x: x["evalue"])

    return results
