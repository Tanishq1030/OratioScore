# Phase 2 — Deterministic Scoring Engine & NLP Pipeline

## Overview
Phase 2 implements the core scoring logic required for the Nirmaan AI Case Study. This includes rule-based scoring, semantic similarity, length penalties, rubric weighting, and structured evidence generation.

---

## Objectives
- Implement real scoring pipeline.
- Integrate rubric.xlsx data.
- Add semantic similarity using sentence-transformers.
- Add fuzzy keyword matching.
- Compute per-criterion & overall scores.
- Produce evidence object for feedback engine.
- Expand tests.

---

## Deliverables

### 1. Scoring Engine (`scoring.py`)
- Keyword scoring (exact + fuzzy).
- Semantic similarity using `all-MiniLM-L6-v2`.
- Length penalties:
  - Below min → -10
  - Above max → -5
- Weighted scoring:
  raw = (0.4 * keyword_score) + (0.6 * semantic_score) + length_penalty
  weighted = raw * (criterion_weight / total_weight)
  overall = sum(weighted_scores), bounded 0–100

### 2. NLP Utilities (`nlp_utils.py`)
- Text cleanup.
- Tokenization.
- Embedding model loader (cached).
- `cosine_sim` implementation.
- Fuzzy keyword matching (RapidFuzz).

### 3. Rubric Loader
- Excel ingestion.
- Keyword normalization.
- Weight validation.
- Caching of rubric description embeddings.

### 4. Evidence Structure
Used for LLM textual feedback:
```
{
  "criterion_name": {
    "keyword_score": ...,
    "semantic_score": ...,
    "length_penalty": ...,
    "raw_score": ...
  }
}
```

### 5. Tests
`test_scoring.py` updated to validate:
- score ranges
- structure
- evidence consistency

## Phase Completion Criteria
- `/score` returns real weighted scores.
- Tests pass fully.
- `rubric.xlsx` is loaded successfully.
- Semantic model loads and embeddings computed.
