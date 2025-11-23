# backend/app/nlp_utils.py
import os
import re
from typing import List, Optional, Tuple
import numpy as np
from functools import lru_cache

# optional fuzzy matching
try:
    from rapidfuzz.fuzz import ratio as fuzzy_ratio  # type: ignore
except Exception:
    fuzzy_ratio = None  # type: ignore

# embeddings
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def clean_text(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def tokenize_words(text: str) -> List[str]:
    text = clean_text(text).lower()
    words = re.findall(r"\b\w+\b", text)
    return words


def count_words(text: str) -> int:
    return len(tokenize_words(text))


def find_keywords_exact(text: str, keywords: List[str]) -> List[str]:
    text_lower = clean_text(text).lower()
    found = []
    for kw in keywords:
        if not kw:
            continue
        if re.search(rf"\b{re.escape(kw.lower())}\b", text_lower):
            found.append(kw)
    return found


def find_keywords_fuzzy(
    text: str, keywords: List[str], threshold: int = 85
) -> List[str]:
    """
    Fuzzy matching fallback — returns keywords where fuzzy match >= threshold.
    Requires rapidfuzz; if not installed, falls back to exact match.
    """
    if fuzzy_ratio is None:
        return find_keywords_exact(text, keywords)

    text_lower = clean_text(text).lower()
    found = []
    for kw in keywords:
        if not kw:
            continue
        # check exact first
        if re.search(rf"\b{re.escape(kw.lower())}\b", text_lower):
            found.append(kw)
            continue
        # fuzzy: test ratio between keyword and text (or best substring)
        try:
            score = fuzzy_ratio(kw.lower(), text_lower)
        except Exception:
            score = 0
        if score >= threshold:
            found.append(kw)
    return found


# Embedding model loader (singleton)
@lru_cache(maxsize=1)
def load_embedding_model(model_name: Optional[str] = None) -> SentenceTransformer:
    name = model_name or _MODEL_NAME
    allow_fallback = os.getenv("EMBEDDING_ALLOW_FALLBACK", "1").lower() in (
        "1",
        "true",
        "yes",
    )

    # If sentence_transformers is not available, optionally provide a deterministic
    # dummy model that returns zero-vectors. This behavior can be disabled via
    # the env var `EMBEDDING_ALLOW_FALLBACK=0` to force an ImportError in test
    # or production environments that require the real model.
    if SentenceTransformer is None:
        if not allow_fallback:
            raise ImportError(
                "sentence_transformers is not installed and EMBEDDING_ALLOW_FALLBACK=0"
            )

        class _DummyModel:
            def __init__(self, _name, dim: int = 384):
                self.name = _name
                self.dim = dim

            def encode(self, texts, convert_to_numpy=True, show_progress_bar=False):
                if isinstance(texts, str):
                    vec = np.zeros(self.dim, dtype=float)
                    return vec
                # assume iterable
                return [np.zeros(self.dim, dtype=float) for _ in texts]

        return _DummyModel(name)

    model = SentenceTransformer(name)
    return model


def get_embedding(text: str, model: Optional[SentenceTransformer] = None) -> np.ndarray:
    """
    Returns a 1D numpy array embedding for given text.
    """
    m = model or load_embedding_model()
    emb = m.encode(text, convert_to_numpy=True, show_progress_bar=False)
    # ensure 1-d
    return np.array(emb).reshape(-1)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None:
        return 0.0
    if a.shape != b.shape:
        # try to coerce or return 0
        try:
            b = b.reshape(a.shape)
        except Exception:
            return 0.0
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
