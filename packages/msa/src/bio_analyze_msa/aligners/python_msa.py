from pathlib import Path
from typing import Any

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from bio_analyze_core.logging import get_logger

from .base import BaseAligner

logger = get_logger(__name__)


class PythonAligner(BaseAligner):
    """
    Pure Python Multiple Sequence Aligner based on Biopython.
    Implements a basic center-star alignment algorithm.
    WARNING: This is intended as a lightweight fallback. For production or
    large datasets, please use MAFFT or MUSCLE.
    """

    def align(self, input_file: Path, output_file: Path, **kwargs: Any) -> Path:
        """
        Run star alignment on the input file.

        Args:
            input_file: Path to unaligned sequences (FASTA).
            output_file: Path to save aligned sequences.
            **kwargs: Ignored.
        """
        logger.warning(
            "Using pure Python star-aligner. This is a basic implementation "
            "and not suitable for large or complex datasets. "
            "Consider installing MAFFT or MUSCLE."
        )

        records = list(SeqIO.parse(input_file, "fasta"))
        if not records:
            raise ValueError(f"No sequences found in {input_file}")

        if len(records) == 1:
            SeqIO.write(records, output_file, "fasta")
            return output_file

        # Center sequence
        ref_id = records[0].id
        ref_seq_orig = str(records[0].seq).upper()

        msa_strings = [ref_seq_orig]
        ids = [ref_id]

        for rec in records[1:]:
            target_seq = str(rec.seq).upper()

            # Since formatting and property extraction are unreliable across Biopython versions,
            # Let's use a very robust pure Python DP implementation for this fallback star aligner
            def align_strings(seq1, seq2):
                # Simple Needleman-Wunsch
                match_score = 1
                mismatch_score = -1
                gap_penalty = -1

                n = len(seq1)
                m = len(seq2)

                # To save memory, use two rows only for scoring
                # But we need full traceback, so we must use a full matrix for large sequences.
                # However, for 200 length it's fine.
                score = [[0] * (m + 1) for _ in range(n + 1)]

                for i in range(n + 1):
                    score[i][0] = gap_penalty * i
                for j in range(m + 1):
                    score[0][j] = gap_penalty * j

                for i in range(1, n + 1):
                    for j in range(1, m + 1):
                        match = score[i - 1][j - 1] + (match_score if seq1[i - 1] == seq2[j - 1] else mismatch_score)
                        delete = score[i - 1][j] + gap_penalty
                        insert = score[i][j - 1] + gap_penalty
                        score[i][j] = max(match, delete, insert)

                # Traceback
                align1 = []
                align2 = []
                i = n
                j = m
                while i > 0 or j > 0:
                    if (
                        i > 0
                        and j > 0
                        and score[i][j]
                        == score[i - 1][j - 1] + (match_score if seq1[i - 1] == seq2[j - 1] else mismatch_score)
                    ):
                        align1.append(seq1[i - 1])
                        align2.append(seq2[j - 1])
                        i -= 1
                        j -= 1
                    elif i > 0 and score[i][j] == score[i - 1][j] + gap_penalty:
                        align1.append(seq1[i - 1])
                        align2.append("-")
                        i -= 1
                    else:
                        align1.append("-")
                        align2.append(seq2[j - 1])
                        j -= 1

                return "".join(reversed(align1)), "".join(reversed(align2))

            # Note: For multiple sequence alignment (center-star method),
            # we need to accumulate the alignment length properly.
            # But wait, earlier when we wrote back `SeqRecord` using Biopython `SeqIO.write`,
            # if `msa_strings` contain empty strings because of some error, it would output just the headers.
            # Let's check `msa_strings`

            new_ref_aligned, new_seq_aligned = align_strings(ref_seq_orig.replace("-", ""), target_seq)

            old_ref = msa_strings[0]
            merged_msa_strings = ["" for _ in range(len(msa_strings))]
            merged_new_str = ""

            i = 0  # index in old_ref
            j = 0  # index in new_ref_aligned

            while i < len(old_ref) or j < len(new_ref_aligned):
                c_old = old_ref[i] if i < len(old_ref) else None
                c_new = new_ref_aligned[j] if j < len(new_ref_aligned) else None

                if c_old == "-":
                    for k in range(len(msa_strings)):
                        merged_msa_strings[k] += msa_strings[k][i]
                    merged_new_str += "-"
                    i += 1
                elif c_new == "-":
                    for k in range(len(msa_strings)):
                        merged_msa_strings[k] += "-"
                    merged_new_str += new_seq_aligned[j]
                    j += 1
                else:
                    # Both are non-gaps, which means they are the same character from the original un-gapped reference
                    for k in range(len(msa_strings)):
                        merged_msa_strings[k] += msa_strings[k][i]
                    merged_new_str += new_seq_aligned[j]
                    i += 1
                    j += 1

            msa_strings = merged_msa_strings
            msa_strings.append(merged_new_str)
            ids.append(rec.id)

            # Update the reference to the newly gapped version
            ref_seq_orig = msa_strings[0]

        # VERY IMPORTANT: write actual records
        aligned_records = []
        for seq_str, seq_id in zip(msa_strings, ids, strict=False):
            # Print sequence to make sure it's not empty
            logger.debug(f"Writing {seq_id}: {len(seq_str)} chars")
            # We must use a simple trick, biopython's SeqIO.write sometimes fails
            # silently if sequence is too long or contains weird characters without warning,
            # but usually it's fine. Let's just write manually to be absolutely sure.
            aligned_records.append(SeqRecord(Seq(seq_str), id=seq_id, description=""))

        with open(output_file, "w", encoding="utf-8") as f:
            for rec in aligned_records:
                f.write(f">{rec.id}\n")
                # Wrap sequence to 80 chars
                seq = str(rec.seq)
                for i in range(0, len(seq), 80):
                    f.write(seq[i : i + 80] + "\n")

        logger.info(f"Python star alignment saved to {output_file}")
        return output_file
