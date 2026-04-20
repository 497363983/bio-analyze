try:
    from Bio.Seq import Seq
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

# 标准 DNA/RNA 互补字典，支持模糊碱基 (IUPAC codes)
_COMPLEMENT_TRANS = str.maketrans(
    "ACGTRYSWKMBDHVNacgtryswkmbdhvnUu",
    "TGCAYRSWMKVHDBNtgcayrswmkvhdbnAa"
)

def reverse_complement(sequence: str, is_rna: bool = False) -> str:
    """
    Calculate the reverse complement of the input sequence.

    Args:
        sequence (str):
            Input nucleic acid sequence.
        is_rna (bool):
            Whether the sequence is RNA. If True, returns a sequence with U instead of T.

    Returns:
        str:
            Reverse complement sequence.
    """
    if not sequence:
        return ""

    if HAS_BIOPYTHON:
        # 使用 Biopython
        seq_obj = Seq(sequence)
        rev_comp = str(seq_obj.reverse_complement())
        # Biopython 的 reverse_complement 默认不将 RNA 的 A 转为 U，除非我们指定类型，
        # 在新版 Biopython 中，Seq() 不再接受 alphabet，而是有专门的 reverse_complement_rna()
        if is_rna:
            try:
                rev_comp = str(seq_obj.reverse_complement_rna())
            except AttributeError:
                # 兼容旧版本 Biopython 逻辑或降级为标准替换
                rev_comp = rev_comp.replace("T", "U").replace("t", "u")
        return rev_comp
    else:
        # 使用 Python 标准库进行兜底
        # 1. 互补
        comp = sequence.translate(_COMPLEMENT_TRANS)
        # 2. 反向
        rev_comp = comp[::-1]

        if is_rna:
            rev_comp = rev_comp.replace("T", "U").replace("t", "u")

        return rev_comp

def complement(sequence: str, is_rna: bool = False) -> str:
    """
    Calculate the complement of the input sequence (without reversing).

    Args:
        sequence (str):
            Input nucleic acid sequence.
        is_rna (bool):
            Whether the sequence is RNA.

    Returns:
        str:
            Complement sequence.
    """
    if not sequence:
        return ""

    if HAS_BIOPYTHON:
        seq_obj = Seq(sequence)
        comp = str(seq_obj.complement())
        if is_rna:
            try:
                comp = str(seq_obj.complement_rna())
            except AttributeError:
                comp = comp.replace("T", "U").replace("t", "u")
        return comp
    else:
        comp = sequence.translate(_COMPLEMENT_TRANS)
        if is_rna:
            comp = comp.replace("T", "U").replace("t", "u")
        return comp
