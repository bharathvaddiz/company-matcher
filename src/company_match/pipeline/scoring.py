from rapidfuzz import fuzz
from metaphone import doublemetaphone

def es_confidence(hits):
    if not hits: return None, 0.0
    b = hits[0]
    top = b["_score"]
    if len(hits)==1: return b, 1.0
    nxt = hits[1]["_score"]
    return b, top/max(top, nxt)


def string_similarity(q, hits):
    best=None; score=0
    for h in hits:
        v = fuzz.ratio(q.lower(), h["_source"]["company_name"].lower())
        if v>score: best=h; score=v
    return best, score


def phonetic_similarity(q, hits):
    if not hits: return None,0
    qp,qa = doublemetaphone(q)
    best=None;score=0
    for h in hits:
        np,na = doublemetaphone(h["_source"]["company_name"])
        sc=0
        if qp == np: sc+=70
        if qa == np: sc+=60
        if qp == na: sc+=50
        if sc>score: best=h;score=sc
    return best,score


def combined_score(es_c, str_s, ph_s):
    # weighted
    return 0.6*es_c + 0.3*(str_s/100) + 0.1*(ph_s/100)

