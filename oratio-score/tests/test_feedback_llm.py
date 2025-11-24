import pytest

import app.feedback_llm as fb


SAMPLE_TRANSCRIPT = [
    {
        "name": "Content",
        "keywords_found": ["coding"],
        "semantic_score": 75.0,
        "raw_score": 80.0,
    },
    {
        "name": "Delivery",
        "keywords_found": [],
        "semantic_score": 40.0,
        "raw_score": 30.0,
    },
]


def test_generate_feedback_simple():
    out = fb.generate_feedback_simple(SAMPLE_TRANSCRIPT)
    assert isinstance(out, dict)
    assert "Content" in out
    assert "Delivery" in out
    for v in out.values():
        assert "evaluation" in v and "suggestion" in v and "justification" in v


def test_generate_feedback_llm_fallback_when_no_llm(monkeypatch):
    # Force LLM unavailable
    monkeypatch.setattr(fb, "LLM_AVAILABLE", False)
    out = fb.generate_feedback_llm(SAMPLE_TRANSCRIPT)
    assert isinstance(out, dict)
    assert "Content" in out and "Delivery" in out


def test_generate_feedback_llm_invalid_llm_output(monkeypatch):
    # Simulate LLM available but returning invalid JSON
    monkeypatch.setattr(fb, "LLM_AVAILABLE", True)
    monkeypatch.setattr(fb, "LLM_TYPE", "openai")

    class DummyLLM:
        def __init__(self, *a, **k):
            pass

    class DummyChain:
        def __init__(self, llm=None, prompt=None):
            pass

        def run(self, **kwargs):
            return "this is not json"

    monkeypatch.setattr(fb, "OpenAI", DummyLLM, raising=False)
    monkeypatch.setattr(fb, "LLMChain", DummyChain, raising=False)
    # avoid requiring PromptTemplate from langchain
    monkeypatch.setattr(fb, "_build_prompt_and_parser", lambda: None, raising=False)

    out = fb.generate_feedback_llm(SAMPLE_TRANSCRIPT)
    # Should fallback to deterministic
    assert isinstance(out, dict)
    assert "Content" in out and "Delivery" in out


def test_generate_feedback_llm_valid_llm_output(monkeypatch):
    # Simulate LLM available and returning valid JSON
    monkeypatch.setattr(fb, "LLM_AVAILABLE", True)
    monkeypatch.setattr(fb, "LLM_TYPE", "openai")

    valid = [
        {
            "criterion": "Content",
            "evaluation": "Good.",
            "suggestion": "Add example.",
            "justification": "Keywords found.",
        },
        {
            "criterion": "Delivery",
            "evaluation": "Average.",
            "suggestion": "Speak louder.",
            "justification": "Pacing slow.",
        },
    ]

    class DummyLLM:
        def __init__(self, *a, **k):
            pass

    class DummyChain:
        def __init__(self, llm=None, prompt=None):
            pass

        def run(self, **kwargs):
            return json.dumps(valid)

    monkeypatch.setattr(fb, "OpenAI", DummyLLM, raising=False)
    monkeypatch.setattr(fb, "LLMChain", DummyChain, raising=False)
    monkeypatch.setattr(fb, "_build_prompt_and_parser", lambda: None, raising=False)

    out = fb.generate_feedback_llm(SAMPLE_TRANSCRIPT)
    assert isinstance(out, dict)
    assert out.get("Content") and out.get("Delivery")
