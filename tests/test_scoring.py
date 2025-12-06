from company_match.pipeline.scoring import combined_score

def test_score():
    sc = combined_score(0.9,80,60)
    assert sc > 0.6
