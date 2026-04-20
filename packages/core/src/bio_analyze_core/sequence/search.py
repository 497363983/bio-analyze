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
    Search for the query sequence in the target sequence, returning all matched start and end indices.

    Args:
        query (str):
            The query sequence to search for.
        target (str):
            The target long sequence.
        allow_ambiguous (bool):
            Whether to allow IUPAC ambiguous bases in the query sequence (e.g., N for any base).

    Returns:
        List[Tuple[int, int]]:
            List containing all match positions (start_index, end_index). 0-based indexing.
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
