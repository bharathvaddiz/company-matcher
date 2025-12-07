"""
Scoring utilities used to evaluate candidate company matches.

This module implements three complementary signals:
- es_confidence: how dominant the top Elasticsearch hit is relative to the next hit.
- string_similarity: character-level similarity using rapidfuzz (0-100).
- phonetic_similarity: token-level phonetic comparison using Double Metaphone.

It also exposes combined_score, which composes these signals into a single
normalized confidence value in [0,1] using fixed weights.
"""

# rapidfuzz provides fast fuzzy string ratios similar to fuzzywuzzy.
from rapidfuzz import fuzz

# doublemetaphone gives phonetic encodings; each call returns up to two codes.
from metaphone import doublemetaphone


def es_confidence(hits):
    """
    Compute a simple ES-based confidence that the top hit is a dominant choice.

    Heuristic:
      - If there are no hits: return (None, 0.0)
      - If there is exactly one hit: return (hit, 1.0) indicating full confidence
      - Otherwise compute top / max(top, next) which yields a value in (0,1]
        that approaches 1 when the top score is much higher than the runner-up.

    Args:
        hits (list): Elasticsearch hit objects ordered by _score desc.

    Returns:
        tuple: (best_hit_or_None, confidence_float)
    """
    if not hits:
        return None, 0.0

    b = hits[0]
    top = b["_score"]

    # Single hit -> maximal confidence
    if len(hits) == 1:
        return b, 1.0

    # Compare to the next-best hit to estimate dominance.
    nxt = hits[1]["_score"]

    # top/max(top, nxt) yields 1.0 when top >= nxt; otherwise ratio < 1.
    return b, top / max(top, nxt)


def string_similarity(q, hits):
    """
    Find the hit with the highest character-level similarity to the query.

    Uses rapidfuzz.fuzz.ratio which returns integer similarity in [0,100].

    Args:
        q (str): Query string.
        hits (list): ES hits with '_source' -> 'company_name'.

    Returns:
        tuple: (best_hit_or_None, best_score_int_0_100)
    """
    best = None
    score = 0
    for h in hits:
        # Compare lowercase forms to reduce case-induced differences.
        v = fuzz.ratio(q.lower(), h["_source"]["company_name"].lower())
        if v > score:
            best = h
            score = v
    return best, score


def phonetic_similarity(q, hits):
    """
    Compute a simple phonetic similarity score using Double Metaphone.

    Approach/heuristic:
      - Compute primary & alternate metaphone codes for the query.
      - For each hit, compute its metaphone codes and award points when codes match:
          * primary_primary match: +70
          * alternate_primary match: +60
          * primary_alternate match: +50
      - Keep the hit with the highest accumulated phonetic score.

    Notes:
      - The numeric scale here is arbitrary (sum of fixed bonuses) and is later
        normalized by combined_score (which divides by 100 for the ph_s term).
      - If there are no hits, returns (None, 0).

    Args:
        q (str): Query string.
        hits (list): ES hits.

    Returns:
        tuple: (best_hit_or_None, score_int)
    """
    if not hits:
        return None, 0

    # doublemetaphone returns a tuple: (primary_code, alternate_code_or_empty)
    qp, qa = doublemetaphone(q)

    best = None
    score = 0
    for h in hits:
        np, na = doublemetaphone(h["_source"]["company_name"])
        sc = 0
        # Award points for different types of metaphone matches.
        if qp == np:
            sc += 70
        if qa == np:
            sc += 60
        if qp == na:
            sc += 50

        if sc > score:
            best = h
            score = sc

    return best, score


def combined_score(es_c, str_s, ph_s):
    """
    Combine ES, string, and phonetic signals into a single confidence score in [0,1].

    Weights (heuristic):
      - ES confidence: 60%
      - string similarity: 30% (expects str_s in 0-100, divide by 100)
      - phonetic similarity: 10% (expects ph_s in 0-100-ish, divide by 100)

    This function preserves the original weighting and normalization:
      combined = 0.6*es_c + 0.3*(str_s/100) + 0.1*(ph_s/100)

    Args:
        es_c (float): ES confidence in [0,1]
        str_s (int): String similarity in [0,100]
        ph_s (int): Phonetic score (heuristic scale, typically 0-130)

    Returns:
        float: normalized combined confidence in [0,1]
    """
    # Weighted linear combination; keep same numeric weights as before.
    return 0.6 * es_c + 0.3 * (str_s / 100) + 0.1 * (ph_s / 100)
