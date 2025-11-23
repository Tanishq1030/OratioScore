# backend/app/scoring.py
from typing import List, Dict, Tuple
from app.nlp_utils import count_words, find_keywords
from app.rubric_loader import load_rubric


def keyword_score(text: str, keywords: List[str]) -> Tuple[float, List[str]]:
    """
    Simple metric: matched / total * 100
    """
    if not keywords:
        return 0.0, []
    matched = find_keywords(text, keywords)
    score = (len(matched) / len(keywords)) * 100
    return score, matched


def length_penalty(
    word_count: int, min_words: int | None, max_words: int | None
) -> float:
    if min_words and word_count < min_words:
        return -10.0
    if max_words and word_count > max_words:
        return -5.0
    return 0.0


def semantic_score_placeholder(text: str, description: str) -> float:
    """
    Placeholder; real semantic similarity (embeddings) will be added in Phase 2.
    For Phase 1 we return 50.0 as neutral baseline.
    """
    return 50.0


def score_transcript_basic(text: str, rubric_path: str | None = None) -> Dict:
    rubric = load_rubric(rubric_path)
    word_count = count_words(text)
    results = []
    overall = 0.0
    total_weight = sum(r["weight"] for r in rubric) or 100.0
    for r in rubric:
        kscore, matched = keyword_score(text, r["keywords"])
        sscore = semantic_score_placeholder(text, r["description"])
        penalty = length_penalty(word_count, r.get("min_words"), r.get("max_words"))
        raw = (0.4 * kscore) + (0.6 * sscore) + penalty
        weighted = raw * (r["weight"] / total_weight)
        results.append(
            {
                "name": r["name"],
                "keyword_score": kscore,
                "keywords_found": matched,
                "semantic_score": sscore,
                "length_penalty": penalty,
                "raw_score": raw,
                "weighted_score": weighted,
            }
        )
        overall += weighted
    overall = max(0.0, min(100.0, overall))
    return {"overall_score": overall, "word_count": word_count, "criteria": results}
