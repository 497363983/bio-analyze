

def smith_waterman(
    query: str,
    subject: str,
    match_score: int = 2,
    mismatch_penalty: int = -1,
    gap_penalty: int = -2
) -> tuple[int, str, str, int, int]:
    """
    zh: 简易的 Smith-Waterman 局部比对算法。
    en: Simple Smith-Waterman local alignment algorithm.

    Args:
        query (str): 查询序列 / Query sequence.
        subject (str): 目标序列 / Subject sequence.
        match_score (int): 匹配得分 / Match score.
        mismatch_penalty (int): 错配罚分 / Mismatch penalty.
        gap_penalty (int): 空位罚分 / Gap penalty.

    Returns:
        Tuple[int, str, str, int, int]:
            - max_score: 最高得分 / Maximum score
            - align_query: 比对后的查询序列 / Aligned query sequence
            - align_subject: 比对后的目标序列 / Aligned subject sequence
            - identity: 匹配的碱基数 / Number of identical bases
            - align_len: 比对总长度 / Total alignment length
    """
    if not query or not subject:
        return 0, "", "", 0, 0

    m, n = len(query), len(subject)

    # Initialize score matrix and traceback matrix
    # scores[i][j] stores the max score at query[i-1] and subject[j-1]
    scores = [[0] * (n + 1) for _ in range(m + 1)]
    # traceback[i][j]: 0=stop, 1=diag(match/mismatch), 2=up(gap in subject), 3=left(gap in query)
    traceback = [[0] * (n + 1) for _ in range(m + 1)]

    max_score = 0
    max_i, max_j = 0, 0

    # Fill matrices
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if query[i - 1].upper() == subject[j - 1].upper():
                diag_score = scores[i - 1][j - 1] + match_score
            else:
                diag_score = scores[i - 1][j - 1] + mismatch_penalty

            up_score = scores[i - 1][j] + gap_penalty
            left_score = scores[i][j - 1] + gap_penalty

            # Local alignment: scores can't be negative
            cell_score = max(0, diag_score, up_score, left_score)
            scores[i][j] = cell_score

            if cell_score == 0:
                traceback[i][j] = 0
            elif cell_score == diag_score:
                traceback[i][j] = 1
            elif cell_score == up_score:
                traceback[i][j] = 2
            else:
                traceback[i][j] = 3

            if cell_score > max_score:
                max_score = cell_score
                max_i, max_j = i, j

    if max_score == 0:
        return 0, "", "", 0, 0

    # Traceback
    align_q = []
    align_s = []
    i, j = max_i, max_j
    identity = 0

    while scores[i][j] > 0:
        if traceback[i][j] == 1:
            q_char = query[i - 1]
            s_char = subject[j - 1]
            align_q.append(q_char)
            align_s.append(s_char)
            if q_char.upper() == s_char.upper():
                identity += 1
            i -= 1
            j -= 1
        elif traceback[i][j] == 2:
            align_q.append(query[i - 1])
            align_s.append("-")
            i -= 1
        elif traceback[i][j] == 3:
            align_q.append("-")
            align_s.append(subject[j - 1])
            j -= 1
        else:
            break

    align_q.reverse()
    align_s.reverse()

    align_query = "".join(align_q)
    align_subject = "".join(align_s)
    align_len = len(align_query)

    return max_score, align_query, align_subject, identity, align_len
