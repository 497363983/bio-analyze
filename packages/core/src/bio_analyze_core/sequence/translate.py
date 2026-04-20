try:
    from Bio.Seq import Seq
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

# 标准遗传密码表 (DNA)
STANDARD_CODON_TABLE = {
    'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
    'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
    'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
    'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
    'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
    'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
    'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
    'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
    'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
    'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
    'TAC': 'Y', 'TAT': 'Y', 'TAA': '*', 'TAG': '*',
    'TGC': 'C', 'TGT': 'C', 'TGA': '*', 'TGG': 'W',
}

def translate(sequence: str, is_rna: bool = False, to_stop: bool = False) -> str:
    """
    Translate nucleic acid sequence to protein sequence.

    Args:
        sequence (str):
            Input DNA or RNA sequence.
        is_rna (bool):
            Whether the sequence is RNA. If True, replaces U with T before translation.
        to_stop (bool):
            Whether to stop translation at the first stop codon (excluding the stop character).

    Returns:
        str:
            Translated protein sequence.
    """
    if not sequence:
        return ""

    if HAS_BIOPYTHON:
        # Biopython translate
        seq_obj = Seq(sequence)
        try:
            return str(seq_obj.translate(to_stop=to_stop))
        except Exception:
            # 对于包含非法字符的情况，Biopython可能会抛错，可以回退到我们自己的实现或者直接抛出
            pass

    # 兜底实现
    seq = sequence.upper()
    if is_rna or "U" in seq:
        seq = seq.replace("U", "T")

    protein = []
    # 按照 3 个碱基步长遍历
    for i in range(0, len(seq) - len(seq) % 3, 3):
        codon = seq[i:i+3]
        aa = STANDARD_CODON_TABLE.get(codon, "X")  # 未知或模糊密码子翻译为 X
        if aa == "*":
            if to_stop:
                break
            protein.append("*")
        else:
            protein.append(aa)

    return "".join(protein)
