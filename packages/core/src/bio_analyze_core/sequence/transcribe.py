try:
    from Bio.Seq import Seq
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

def transcribe(sequence: str) -> str:
    """
    zh: 将 DNA 序列转录为 RNA 序列 (将 T 替换为 U)。
    en: Transcribe DNA sequence to RNA sequence (replace T with U).

    Args:
        sequence (str):
            zh: 输入的 DNA 序列。
            en: Input DNA sequence.

    Returns:
        str:
            zh: 转录后的 RNA 序列。
            en: Transcribed RNA sequence.
    """
    if not sequence:
        return ""

    if HAS_BIOPYTHON:
        return str(Seq(sequence).transcribe())
    else:
        return sequence.replace("T", "U").replace("t", "u")


def reverse_transcribe(sequence: str) -> str:
    """
    zh: 将 RNA 序列逆转录为 DNA 序列 (将 U 替换为 T)。
    en: Reverse transcribe RNA sequence to DNA sequence (replace U with T).

    Args:
        sequence (str):
            zh: 输入的 RNA 序列。
            en: Input RNA sequence.

    Returns:
        str:
            zh: 逆转录后的 DNA 序列。
            en: Reverse transcribed DNA sequence.
    """
    if not sequence:
        return ""

    if HAS_BIOPYTHON:
        return str(Seq(sequence).back_transcribe())
    else:
        return sequence.replace("U", "T").replace("u", "t")
