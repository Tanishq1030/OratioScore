# Scoring Formula — Phase 2 (finalized)

This document defines the deterministic scoring logic implemented in Phase 2.

Inputs
- transcript (text)
- rubric.xlsx rows with fields:
  - Criterion Name
  - Description
  - Keywords (comma-separated)
  - Weight (numeric)
  - Min Words (optional)
  - Max Words (optional)

Pipeline
1. Preprocessing
   - Clean text, tokenize, count words.

2. Rule-based keyword score
   - For each criterion:
     - `keyword_score = (number_of_matched_keywords / total_keywords) * 100`
     - Matching uses exact word-boundary match; if none found and `rapidfuzz` is installed, fuzzy matching with threshold 85 is attempted.

3. Semantic similarity
   - Compute transcript embedding and criterion description embedding with `sentence-transformers/all-MiniLM-L6-v2`.
   - `semantic_score = cosine_similarity(transcript_emb, criterion_emb) * 100`

4. Length penalties
   - if `words < min_words` → penalty = -10
   - if `words > max_words` → penalty = -5
   - else penalty = 0

5. Per-criterion raw score
   - `raw_score = (KEYWORD_WEIGHT * keyword_score) + (SEMANTIC_WEIGHT * semantic_score) + length_penalty`
   - Default weights:
     - `KEYWORD_WEIGHT = 0.4`
     - `SEMANTIC_WEIGHT = 0.6`
   - `raw_score` is clamped to `[0, 100]` for presentation.

6. Weighted and overall score
   - `weighted_score = raw_score * (criterion_weight / sum(all_weights))`
   - `overall_score = sum(weighted_score for all criteria)` then clamped to `[0, 100]`.

Notes
- All numeric operations use floats; rounding is applied for display.
- The LLM (LangChain) is used only to generate textual feedback and justification from the evidence (keyword hits, semantic scores, penalties). LLM output is not used to change numeric scores.
