This backend contains utilities for scoring transcripts using keyword and semantic matching.

Embedding model fallback
 - The code uses `sentence-transformers` for embeddings when available.
 - For lightweight development and in CI where installing the heavy model is undesirable,
	 the code can fall back to a deterministic dummy model that returns zero-vectors.
 - Control the fallback behavior with the environment variable `EMBEDDING_ALLOW_FALLBACK`:
	 - `1` (default): allow fallback (returns zero vectors when `sentence-transformers` is not installed).
	 - `0`: disable fallback and raise `ImportError` if the real embedding library is missing.

Tests
 - A unit test ensures the fallback model produces deterministic zero vectors
	 (`tests/test_nlp_fallback.py`).

Recommendation
 - For production or realistic scoring, install `sentence-transformers` and provide
	 a proper embedding model via `EMBEDDING_MODEL` environment variable.
