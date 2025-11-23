# tests/test_nlp_fallback.py
import os
import numpy as np
import pytest

import app.nlp_utils as nlp


def teardown_function():
    # ensure cache cleared between tests
    try:
        nlp.load_embedding_model.cache_clear()
    except Exception:
        pass


def test_dummy_model_enabled(monkeypatch):
    # enable fallback
    monkeypatch.setenv("EMBEDDING_ALLOW_FALLBACK", "1")
    # simulate sentence_transformers missing
    monkeypatch.setattr(nlp, "SentenceTransformer", None)
    nlp.load_embedding_model.cache_clear()

    model = nlp.load_embedding_model()
    emb = nlp.get_embedding("hello world", model=model)
    assert isinstance(emb, np.ndarray)
    assert emb.size == 384
    assert np.all(emb == 0.0)


def test_fallback_disabled_raises(monkeypatch):
    monkeypatch.setenv("EMBEDDING_ALLOW_FALLBACK", "0")
    monkeypatch.setattr(nlp, "SentenceTransformer", None)
    nlp.load_embedding_model.cache_clear()

    with pytest.raises(ImportError):
        nlp.load_embedding_model()
