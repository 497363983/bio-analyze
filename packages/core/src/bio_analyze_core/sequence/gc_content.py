try:
    from Bio.SeqUtils import gc_fraction
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

def gc_content(sequence: str, ignore_n: bool = True) -> float:
    """
    Calculate the GC content of the sequence.

    Args:
        sequence (str):
            Input nucleic acid sequence.
        ignore_n (bool):
            如果使用 Biopython，该参数将被忽略，因为 gc_fraction 内部有自己的处理逻辑
            （通常计算 G+S+C 占全长的比例）。
            Whether to ignore 'N' or other ambiguous bases in total length. Default is True.

    Returns:
        float:
            GC content fraction (between 0.0 and 1.0). Returns 0.0 if sequence is empty.
    """
    if not sequence:
        return 0.0

    if HAS_BIOPYTHON:
        # Biopython 的 gc_fraction 返回的是 0-1 的比例
        # 较老版本的 Biopython 使用 GC(seq) 返回百分比 0-100
        try:
            return float(gc_fraction(sequence))
        except NameError:
            # 兼容旧版本
            from Bio.SeqUtils import GC
            return GC(sequence) / 100.0
    else:
        # 标准库兜底计算
        seq = sequence.upper()
        g_count = seq.count("G")
        c_count = seq.count("C")
        s_count = seq.count("S") # 强配对 (G或C)

        gc_total = g_count + c_count + s_count

        if ignore_n:
            a_count = seq.count("A")
            t_count = seq.count("T")
            u_count = seq.count("U")
            w_count = seq.count("W") # 弱配对 (A或T)
            valid_total = gc_total + a_count + t_count + u_count + w_count
            if valid_total == 0:
                return 0.0
            return gc_total / valid_total
        else:
            return gc_total / len(sequence)
