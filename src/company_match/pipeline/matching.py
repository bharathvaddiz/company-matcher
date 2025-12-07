"""
Match entrypoint for company name queries.

This module coordinates:
- querying Elasticsearch for candidate company documents,
- computing three complementary signals (ES score confidence, string
  similarity, phonetic similarity),
- combining them into a single weighted confidence score, and
- producing a match decision (accepted/rejected) with reason codes and
  readable confidence level.

Behavior is unchanged; this file only adds documentation and inline comments
to make the decision logic and heuristics explicit.
"""

# Query helper that returns ES hits for the provided query string.
from .es_client import search_es

# Scoring helpers: extract signals from ES hits and compute a combined score.
from .scoring import es_confidence, string_similarity, phonetic_similarity, combined_score

# Structured logger that forwards events to ELK/observability.
from .logging_utils import elk_log

# Thresholds controlling decision boundaries (configured elsewhere).
from .config import THRESHOLD_ACCEPT, THRESHOLD_HIGH


def match(q):
    """
    Attempt to match the input query `q` to a canonical company name.

    Args:
        q (str): Free-text company name to match.

    Returns:
        dict: {
            "match": str|None,          # matched canonical company_name or None
            "confidence": float,        # combined weighted confidence in [0,1]
            "level": "HIGH"/"MEDIUM"/"LOW",  # human-friendly bucket
            "reason": str,              # reason code explaining decision
            "status": "ACCEPTED"/"REJECTED"  # final accept/reject decision
        }
    """
    # Fetch candidate documents from Elasticsearch for the query.
    hits = search_es(q)

    # Compute three complementary signals:
    # - es_confidence: how dominant the top ES hit is relative to the runner-up
    # - string_similarity: character-level similarity (0-100) using rapidfuzz
    # - phonetic_similarity: metaphone-based phonetic score (0-~130 in this impl)
    es_best, es_c = es_confidence(hits)
    st_best, st_s = string_similarity(q, hits)
    ph_best, ph_s = phonetic_similarity(q, hits)

    # Compute a single weighted combined score in [0,1] using configured weights.
    # The scoring helper normalizes string and phonetic terms to fractions.
    combined = combined_score(es_c, st_s, ph_s)

    # Map numeric combined score to a human-friendly bucket for display.
    # These buckets are determined by THRESHOLD_HIGH and THRESHOLD_ACCEPT.
    if combined >= THRESHOLD_HIGH:
        level = "HIGH"
    elif combined >= THRESHOLD_ACCEPT:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Determine a concise reason code for observability/audit about why this
    # match was chosen or why fallback was used. Note: thresholds here are
    # intentionally coarse to make reason codes meaningful.
    if es_c >= THRESHOLD_HIGH:
        # Top ES hit dominates; prefer ES confidence as the justification.
        reason = "HIGH_ES_CONFIDENCE"
    elif st_s >= 65:
        # String similarity (rapidfuzz ratio) is strong enough to be used.
        reason = "STRING_SIMILARITY_USED"
    elif ph_s >= 50:
        # Phonetic similarity provided a plausible fallback match.
        reason = "PHONETIC_FALLBACK_USED"
    else:
        # No strong signal; result is weak.
        reason = "WEAK_MATCH"

    # Final accept/reject decision based on the combined score.
    if combined >= THRESHOLD_ACCEPT:
        # If accepted, return the canonical company_name from the ES top hit
        # (if available). Keep behavior identical to previous implementation.
        result = es_best["_source"]["company_name"] if es_best else None
        status = "ACCEPTED"
    else:
        result = None
        status = "REJECTED"

    # Emit a structured log event for downstream analysis / auditing.
    # Include the raw input, the chosen match, numeric score, textual reason,
    # and the acceptance status. This mirrors the original behavior.
    elk_log(
        "match_decision",
        input=q,
        matched=result,
        score=combined,
        reason=reason,
        level=status
    )

    # Return the decision payload; callers rely on this shape.
    return {
        "match": result,
        "confidence": combined,
        "level": level,
        "reason": reason,
        "status": status,
    }
