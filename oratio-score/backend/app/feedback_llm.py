# backend/app/feedback_llm.py
from typing import List, Dict


def generate_feedback_simple(evidence: List[Dict]) -> Dict[str, Dict]:
    """
    Phase 1 simple feedback generator.
    Returns a dict mapping criterion name -> {evaluation, suggestion, justification}
    """
    out = {}
    for e in evidence:
        name = e["name"]
        kfound = e.get("keywords_found", []) or []
        sscore = e.get("semantic_score", 0.0)
        raw = e.get("raw_score", 0.0)
        if len(kfound) == 0 and sscore < 60:
            eval_text = "Low relevance to this criterion."
            suggestion = "Mention the topic explicitly and give a short example."
        elif len(kfound) > 0 and sscore >= 60:
            eval_text = "Good coverage of this criterion."
            suggestion = "Add a specific example to strengthen it."
        else:
            eval_text = "Partial coverage."
            suggestion = "Expand the relevant points and include keywords."
        justification = f"Keywords found: {kfound}. Semantic score: {sscore:.2f}. Computed raw score: {raw:.1f}."
        out[name] = {
            "evaluation": eval_text,
            "suggestion": suggestion,
            "justification": justification,
        }
    return out
