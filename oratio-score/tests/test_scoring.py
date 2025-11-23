# tests/test_scoring.py
from app.scoring import score_transcript
import math


def test_score_transcript_basic():
    sample = "Hello, I am Tanishq. I like coding, music and sports. I have worked on projects."
    res = score_transcript(sample)
    assert "overall_score" in res
    assert isinstance(res["overall_score"], float)
    assert 0.0 <= res["overall_score"] <= 100.0
    assert "criteria" in res
    assert isinstance(res["criteria"], list)
    # each criterion should contain expected keys
    for c in res["criteria"]:
        assert "name" in c
        assert "keyword_score" in c
        assert "semantic_score" in c
        assert "raw_score" in c
        assert "weighted_score" in c
