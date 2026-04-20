import re


def is_valid_dna(sequence: str, strict: bool = False) -> bool:
    """
    Check if the sequence is a valid DNA sequence.

    Args:
        sequence (str):
            Input sequence string.
        strict (bool):
            If True, only A, C, G, T are allowed. Otherwise, IUPAC ambiguity codes are allowed.

    Returns:
        bool:
            Whether it is a valid DNA sequence.
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
    Check if the sequence is a valid RNA sequence.

    Args:
        sequence (str):
            Input sequence string.
        strict (bool):
            If True, only A, C, G, U are allowed. Otherwise, IUPAC ambiguity codes are allowed.

    Returns:
        bool:
            Whether it is a valid RNA sequence.
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
    Check if the sequence is a valid protein sequence.

    Args:
        sequence (str):
            Input sequence string.

    Returns:
        bool:
            Whether it is a valid protein sequence.
    """
    if not sequence:
        return False

    seq = re.sub(r"\s+", "", sequence)
    if not seq:
        return False

    # 标准氨基酸以及特殊氨基酸/符号 (U=Sec, O=Pyl, X=Unknown, B=Asx, Z=Glx, J=Xle, *=Stop, -=Gap)
    pattern = r"^[ACDEFGHIKLMNPQRSTVWYUOXZBJ\*\-acdefghiklmnpqrstvwyuoxzbj]+$"
    return bool(re.fullmatch(pattern, seq))
