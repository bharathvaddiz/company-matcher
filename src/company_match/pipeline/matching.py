from .es_client import search_es
from .scoring import es_confidence, string_similarity, phonetic_similarity, combined_score
from .logging_utils import elk_log
from .config import THRESHOLD_ACCEPT, THRESHOLD_HIGH


def match(q):
    hits = search_es(q)

    # raw scores
    es_best, es_c = es_confidence(hits)
    st_best, st_s = string_similarity(q, hits)
    ph_best, ph_s = phonetic_similarity(q, hits)

    # weighted combined
    combined = combined_score(es_c, st_s, ph_s)

    # confidence levels
    if combined >= THRESHOLD_HIGH:
        level = "HIGH"
    elif combined >= THRESHOLD_ACCEPT:
        level = "MEDIUM"
    else:
        level = "LOW"

    # reason codes
    if es_c >= THRESHOLD_HIGH:
        reason = "HIGH_ES_CONFIDENCE"
    elif st_s >= 65:
        reason = "STRING_SIMILARITY_USED"
    elif ph_s >= 50:
        reason = "PHONETIC_FALLBACK_USED"
    else:
        reason = "WEAK_MATCH"

    # decision
    if combined >= THRESHOLD_ACCEPT:
        result = es_best["_source"]["company_name"] if es_best else None
        status = "ACCEPTED"
    else:
        result = None
        status = "REJECTED"

    # log
    elk_log(
        "match_decision",
        input=q,
        matched=result,
        score=combined,
        reason=reason,
        level=status
    )

    return {
        "match": result,
        "confidence": combined,
        "level": level,
        "reason": reason,
        "status": status,
    }

