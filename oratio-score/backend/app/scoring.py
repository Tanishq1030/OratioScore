# backend/app/scoring.py
from typing import List, Dict, Tuple, Optional
from app.nlp_utils import (
    count_words,
    find_keywords_exact,
    find_keywords_fuzzy,
    get_embedding,
    cosine_sim,
    load_embedding_model,
)

from app.rubic_loader import load_rubric
import numpy as np
from app.config import settings

_rubric_cache: Optional[List[Dict]] = None
_rubric_embeddings_cache: Optional[np.ndarray] = None


def _prepare_rubric_cache(rubric_path: Optional[str] = None):
    global _rubric_cache, _rubric_embeddings_cache
    if _rubric_cache is not None:
        return
    rubric = load_rubric(rubric_path)
    model = load_embedding_model()
    desc_texts = [r.get("description", "") or "" for r in rubric]
    # compute embeddings for each description
    embs = model.encode(desc_texts, convert_to_numpy=True, show_progress_bar=False)
    _rubric_cache = rubric
    _rubric_embeddings_cache = np.array(embs)


def keyword_score(
    text: str, keywords: List[str], use_fuzzy: bool = True
) -> Tuple[float, List[str]]:
    """
    Returns (score in 0..100, matched_keywords)
    """
    if not keywords:
        return 0.0, []
    # exact match
    found = find_keywords_exact(text, keywords)
    # if nothing found and fuzzy available, try fuzzy
    if use_fuzzy and len(found) == 0:
        found = find_keywords_fuzzy(text, keywords)
    score = (len(found) / len(keywords)) * 100.0
    return score, found


def semantic_score(transcript_emb: np.ndarray, criterion_emb: np.ndarray) -> float:
    """
    Returns semantic similarity converted to 0..100
    """
    sim = cosine_sim(transcript_emb, criterion_emb)
    score = float(sim * 100.0)
    # clamp
    return max(0.0, min(100.0, score))


def length_penalty(
    word_count: int, min_words: Optional[int], max_words: Optional[int]
) -> float:
    if min_words and word_count < min_words:
        return float(settings.LENGTH_PENALTY_UNDER_MIN)
    if max_words and word_count > max_words:
        return float(settings.LENGTH_PENALTY_OVER_MAX)
    return 0.0


def score_transcript(
    text: str, rubric_path: Optional[str] = None, use_fuzzy: bool = True
) -> Dict:
    """
    Full deterministic scoring pipeline.
    Returns:
      {
        "overall_score": float,
        "word_count": int,
        "criteria": [
           {
             name, keyword_score, keywords_found, semantic_score,
             length_penalty, raw_score, weighted_score, weight
           }, ...
        ],
        "evidence": {...}  # same as criteria but keyed by name for LLM use
      }
    """
    _prepare_rubric_cache(rubric_path)
    global _rubric_cache, _rubric_embeddings_cache
    rubric = _rubric_cache or []
    rubric_embs = _rubric_embeddings_cache

    word_count = count_words(text)
    transcript_emb = get_embedding(text)

    total_weight = sum(r["weight"] for r in rubric) or 100.0

    criteria_out = []
    evidence = {}
    overall_weighted = 0.0

    for i, r in enumerate(rubric):
        crit_name = r["name"]
        # keyword
        kscore, matched = keyword_score(
            text, r.get("keywords", []), use_fuzzy=use_fuzzy
        )
        # semantic
        crit_emb = rubric_embs[i]
        sscore = semantic_score(transcript_emb, crit_emb)
        # length penalty
        penalty = length_penalty(word_count, r.get("min_words"), r.get("max_words"))
        # combine weights (configurable weights)
        kw_w = float(settings.KEYWORD_WEIGHT)
        sem_w = float(settings.SEMANTIC_WEIGHT)
        raw = (kw_w * kscore) + (sem_w * sscore) + penalty
        weighted = raw * (r["weight"] / total_weight)
        # clamp raw between 0-100 for readability (but weighted may be <0 if negative penalty present; we keep weighted as-is)
        raw_clamped = max(0.0, min(100.0, raw))
        criteria_out.append(
            {
                "name": crit_name,
                "weight": r["weight"],
                "keyword_score": float(round(kscore, 3)),
                "keywords_found": matched,
                "semantic_score": float(round(sscore, 3)),
                "length_penalty": float(penalty),
                "raw_score": float(round(raw_clamped, 3)),
                "weighted_score": float(round(weighted, 4)),
            }
        )
        evidence[crit_name] = {
            "name": crit_name,
            "description": r.get("description"),
            "weight": r["weight"],
            "keyword_score": float(round(kscore, 3)),
            "keywords_found": matched,
            "semantic_score": float(round(sscore, 3)),
            "length_penalty": float(penalty),
            "raw_score": float(round(raw_clamped, 3)),
        }
        overall_weighted += weighted

    overall_score = float(max(0.0, min(100.0, overall_weighted)))
    return {
        "overall_score": overall_score,
        "word_count": word_count,
        "criteria": criteria_out,
        "evidence": evidence,
    }
