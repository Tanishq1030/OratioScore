"""
This file provides:
- basic text cleaning/tokenization utilities
- keyword matching (exact + fuzzy via rapidfuzz)
- a Render-safe embedding model loader with small-model preference,
  lazy singleton loading, and deterministic dummy fallback
- embedding helpers and cosine similarity

Notes:
- To avoid OOM on small hosts (Render free tier), the loader prefers
  "paraphrase-MiniLM-L3-v2" by default. You can override with the
  EMBEDDING_MODEL environment variable.
- If sentence-transformers is not installed (e.g., tests), a dummy
  deterministic zero-vector model is used unless EMBEDDING_ALLOW_FALLBACK=0.
"""

import os
import re
from typing import List, Optional, Tuple
import numpy as np
from functools import lru_cache
from threading import Lock

# optional fuzzy matching (rapidfuzz)
try:
    from rapidfuzz.fuzz import ratio as fuzzy_ratio  # type: ignore
except Exception:
    fuzzy_ratio = None  # type: ignore

# embeddings (optional import)
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None  # type: ignore

# Default model name (can be overridden via ENV)
# NOTE: default kept as a robust model, but loader below prefers a tiny model
_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def clean_text(text: str) -> str:
    """
    Basic whitespace normalization and trimming.
    """
    if not text:
        return ""
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def tokenize_words(text: str) -> List[str]:
    """
    Lowercase tokenization into alphanumeric words.
    """
    text = clean_text(text).lower()
    words = re.findall(r"\b\w+\b", text)
    return words


def count_words(text: str) -> int:
    """
    Return word count (simple tokenization).
    """
    return len(tokenize_words(text))


def find_keywords_exact(text: str, keywords: List[str]) -> List[str]:
    """
    Find exact keyword matches using word-boundary regex.
    Returns the list of keywords found (preserves original keyword strings).
    """
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
    NOTE: fuzzy_ratio is applied between keyword and full text (cheap fallback),
    which is sufficient for short transcripts and keyword lists.
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
        # fuzzy: compare keyword vs text
        try:
            score = fuzzy_ratio(kw.lower(), text_lower)
        except Exception:
            score = 0
        if score >= threshold:
            found.append(kw)
    return found


# ---------------------------
# Embedding model loader (Render-safe)
# ---------------------------

# Preferred small models (smallest first) to avoid OOM on constrained hosts
_PREFERRED_MODELS = [
    "sentence-transformers/paraphrase-MiniLM-L3-v2",  # very small, Render-friendly
    "sentence-transformers/all-MiniLM-L12-v2",  # medium
    "sentence-transformers/all-MiniLM-L6-v2",  # original / fallback
]

_model = None
_model_lock = Lock()


def _make_dummy_model(dim: int = 384):
    """
    Return a deterministic dummy model that produces zero-vectors.
    Used when sentence-transformers is not available or when fallbacks are allowed.
    """

    class _DummyModel:
        def __init__(self, _dim=dim):
            self.dim = _dim

        def encode(self, texts, convert_to_numpy=True, show_progress_bar=False):
            if isinstance(texts, str):
                return np.zeros(self.dim, dtype=float)
            # assume iterable
            return [np.zeros(self.dim, dtype=float) for _ in texts]

    return _DummyModel()


def load_embedding_model(model_name: Optional[str] = None):
    """
    Lazy, thread-safe loader for the embedding model. Attempts these sources:
      1. environment or passed model_name
      2. preferred small models defined in _PREFERRED_MODELS
      3. deterministic dummy fallback (if allowed)

    Environment flags:
      EMBEDDING_MODEL         -> override model name
      EMBEDDING_ALLOW_FALLBACK -> "0"/"false"/"no" to disable dummy fallback
    """
    global _model

    if _model is not None:
        return _model

    # prefer explicit model_name, then environment, then defaults
    env_model = os.getenv("EMBEDDING_MODEL")
    desired = model_name or env_model or _MODEL_NAME

    allow_fallback = os.getenv("EMBEDDING_ALLOW_FALLBACK", "1").lower() in (
        "1",
        "true",
        "yes",
    )

    # If sentence_transformers is missing, optionally return dummy model
    if SentenceTransformer is None:
        if not allow_fallback:
            raise ImportError(
                "sentence_transformers is not installed and fallback disabled (EMBEDDING_ALLOW_FALLBACK=0)"
            )
        _model = _make_dummy_model()
        return _model

    # Thread-safe lazy initialization
    with _model_lock:
        if _model is not None:
            return _model

        last_exc = None
        # Try the explicitly desired name first, then the preferred list
        candidates = [desired] + [m for m in _PREFERRED_MODELS if m != desired]
        for candidate in candidates:
            try:
                # print/logging to stdout so Render logs show model load attempts
                print(f"[nlp_utils] Attempting to load model: {candidate}")
                _model = SentenceTransformer(candidate)
                print(f"[nlp_utils] Successfully loaded embedding model: {candidate}")
                return _model
            except Exception as e:
                last_exc = e
                print(f"[nlp_utils] Failed to load model {candidate}: {e}")

        # If none loaded, either raise or return deterministic dummy
        if not allow_fallback:
            raise RuntimeError("Failed to load any embedding model") from last_exc

        print("[nlp_utils] Falling back to deterministic dummy embedding model")
        _model = _make_dummy_model()
        return _model


def get_embedding(text: str, model: Optional[object] = None) -> np.ndarray:
    """
    Returns a 1D numpy array embedding for the given text.
    Ensures deterministic 1-D output even for single-string input.
    """
    m = model or load_embedding_model()
    emb = m.encode(text, convert_to_numpy=True, show_progress_bar=False)
    return np.array(emb).reshape(-1)


def embed_batch(texts: List[str], model: Optional[object] = None) -> List[np.ndarray]:
    """
    Encode a batch of texts and return a list of 1D numpy arrays.
    """
    m = model or load_embedding_model()
    embs = m.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # convert to list of 1d np arrays
    return [np.array(e).reshape(-1) for e in embs]


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Cosine similarity between two 1D numpy arrays.
    Returns a float in [-1, 1]. Returns 0.0 for zero vectors or incompatible shapes.
    """
    if a is None or b is None:
        return 0.0
    try:
        a = np.array(a).reshape(-1)
        b = np.array(b).reshape(-1)
    except Exception:
        return 0.0
    if a.shape != b.shape:
        # attempt to coerce shapes or bail
        try:
            b = b.reshape(a.shape)
        except Exception:
            return 0.0
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
