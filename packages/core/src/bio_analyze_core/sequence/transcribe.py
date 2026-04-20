try:
    from Bio.Seq import Seq
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

def transcribe(sequence: str) -> str:
    """
    Transcribe DNA sequence to RNA sequence (replace T with U).

    Args:
        sequence (str):
            Input DNA sequence.

    Returns:
        str:
            Transcribed RNA sequence.
    """
    if not sequence:
        return ""

    if HAS_BIOPYTHON:
        return str(Seq(sequence).transcribe())
    else:
        return sequence.replace("T", "U").replace("t", "u")

def reverse_transcribe(sequence: str) -> str:
    """
    Reverse transcribe RNA sequence to DNA sequence (replace U with T).

    Args:
        sequence (str):
            Input RNA sequence.

    Returns:
        str:
            Reverse transcribed DNA sequence.
    """
    if not sequence:
        return ""

    if HAS_BIOPYTHON:
        return str(Seq(sequence).back_transcribe())
    else:
        return sequence.replace("U", "T").replace("u", "t")
