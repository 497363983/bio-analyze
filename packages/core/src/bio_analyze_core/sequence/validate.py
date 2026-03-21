import re


def is_valid_dna(sequence: str, strict: bool = False) -> bool:
    """
    zh: 检查序列是否为合法的 DNA 序列。
    en: Check if the sequence is a valid DNA sequence.

    Args:
        sequence (str):
            zh: 输入的序列字符串。
            en: Input sequence string.
        strict (bool):
            zh: 如果为 True，则仅允许 A, C, G, T。否则允许 IUPAC 模糊碱基 (如 N, R, Y 等)。
            en: If True, only A, C, G, T are allowed. Otherwise, IUPAC ambiguity codes are allowed.

    Returns:
        bool:
            zh: 是否为合法 DNA 序列。
            en: Whether it is a valid DNA sequence.
    """
    if not sequence:
        return False

    # 忽略空白字符
    seq = re.sub(r"\s+", "", sequence)
    if not seq:
        return False

    pattern = r"^[ACGTacgt]+$" if strict else r"^[ACGTRYSWKMBDHVNacgtryswkmbdhvn\-]+$"

    return bool(re.fullmatch(pattern, seq))


def is_valid_rna(sequence: str, strict: bool = False) -> bool:
    """
    zh: 检查序列是否为合法的 RNA 序列。
    en: Check if the sequence is a valid RNA sequence.

    Args:
        sequence (str):
            zh: 输入的序列字符串。
            en: Input sequence string.
        strict (bool):
            zh: 如果为 True，则仅允许 A, C, G, U。否则允许 IUPAC 模糊碱基。
            en: If True, only A, C, G, U are allowed. Otherwise, IUPAC ambiguity codes are allowed.

    Returns:
        bool:
            zh: 是否为合法 RNA 序列。
            en: Whether it is a valid RNA sequence.
    """
    if not sequence:
        return False

    seq = re.sub(r"\s+", "", sequence)
    if not seq:
        return False

    pattern = r"^[ACGUacgu]+$" if strict else r"^[ACGURYSWKMBDHVNacguryswkmbdhvn\-]+$"

    return bool(re.fullmatch(pattern, seq))


def is_valid_protein(sequence: str) -> bool:
    """
    zh: 检查序列是否为合法的蛋白质序列。
    en: Check if the sequence is a valid protein sequence.

    Args:
        sequence (str):
            zh: 输入的序列字符串。
            en: Input sequence string.

    Returns:
        bool:
            zh: 是否为合法蛋白质序列。
            en: Whether it is a valid protein sequence.
    """
    if not sequence:
        return False

    seq = re.sub(r"\s+", "", sequence)
    if not seq:
        return False

    # 标准氨基酸以及特殊氨基酸/符号 (U=Sec, O=Pyl, X=Unknown, B=Asx, Z=Glx, J=Xle, *=Stop, -=Gap)
    pattern = r"^[ACDEFGHIKLMNPQRSTVWYUOXZBJ\*\-acdefghiklmnpqrstvwyuoxzbj]+$"
    return bool(re.fullmatch(pattern, seq))
