# Phase 4 — LLM Feedback Integration (LangChain)

## Overview
Phase 4 adds high-quality textual feedback using LangChain and OpenAI/Azure models. The LLM enhances interpretability but does NOT influence numeric scoring.

---

## Objectives
- Provide structured, short feedback messages for each rubric criterion.
- Maintain determinism in numeric scoring.
- Use LLM only for text-level guidance.

---

## Deliverables

### 1. `feedback_llm.py` Enhancements
- LangChain-based JSON output.
- Supported providers:
  - AzureOpenAI
  - OpenAI
- `fallback` → deterministic feedback if:
  - keys missing
  - model unavailable
  - parse failure

### 2. Prompt Structure
LLM is instructed to return:
```
{
  "criterion": "",
  "evaluation": "",
  "suggestion": "",
  "justification": ""
}
```

### 3. Integration with Scoring Pipeline
`/score` endpoint returns:
- scores
- evidence
- feedback (LLM-generated or fallback)

## Phase Completion Criteria
- LLM feedback integrated without impacting numeric scores.
- No runtime failures with missing keys.
- Deterministic fallback always available.
