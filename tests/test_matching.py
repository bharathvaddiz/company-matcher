from company_match.pipeline.matching import match

def test_matching_runs():
    r = match("test")
    assert "status" in r
