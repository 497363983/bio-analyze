import re

# IUPAC 模糊碱基到正则表达式的映射 (DNA)
IUPAC_DICT = {
    'A': 'A', 'C': 'C', 'G': 'G', 'T': 'T', 'U': 'U',
    'R': '[AG]', 'Y': '[CTU]', 'S': '[GC]', 'W': '[ATU]',
    'K': '[GTU]', 'M': '[AC]', 'B': '[CGTU]', 'D': '[AGTU]',
    'H': '[ACTU]', 'V': '[ACG]', 'N': '[ACGTU]'
}

def search_sequence(query: str, target: str, allow_ambiguous: bool = False) -> list[tuple[int, int]]:
    """
    zh: 在目标序列中搜索查询序列，返回所有匹配的起始和结束索引。
    en: Search for the query sequence in the target sequence, returning all matched start and end indices.

    Args:
        query (str):
            zh: 要搜索的查询序列。
            en: The query sequence to search for.
        target (str):
            zh: 目标长序列。
            en: The target long sequence.
        allow_ambiguous (bool):
            zh: 是否允许查询序列中包含 IUPAC 模糊碱基（如 N 代表任何碱基）。
            en: Whether to allow IUPAC ambiguous bases in the query sequence (e.g., N for any base).

    Returns:
        List[Tuple[int, int]]:
            zh: 包含所有匹配位置 (start_index, end_index) 的列表。索引从 0 开始。
            en: List containing all match positions (start_index, end_index). 0-based indexing.
    """
    if not query or not target:
        return []

    q = query.upper()
    t = target.upper()

    if not allow_ambiguous:
        # 精确匹配
        results = []
        start = 0
        while True:
            idx = t.find(q, start)
            if idx == -1:
                break
            results.append((idx, idx + len(q)))
            start = idx + 1  # 允许重叠匹配
        return results
    else:
        # 正则表达式匹配，处理模糊碱基
        pattern_str = ""
        for char in q:
            pattern_str += IUPAC_DICT.get(char, char)

        # 使用正则表达式查找（包含重叠匹配）
        pattern = re.compile(f"(?=({pattern_str}))")
        results = []
        for match in pattern.finditer(t):
            start_idx = match.start()
            end_idx = start_idx + len(q)
            results.append((start_idx, end_idx))

        return results
