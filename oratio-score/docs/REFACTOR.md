# Repo structure analysis & refinement suggestions

Current structure (important folders):
- `backend/` → FastAPI backend, app code under `backend/app/`.
- `frontend/` → Streamlit UI.
- `data/` → sample data (rubric.xlsx, uploaded case study files).
- `docs/` → documentation and notes.
- `tests/` → unit and integration tests.

Observations and recommended refinements

1. Package layout consistency
- Move `backend/app` to `backend/src/app` or set `backend` as a package root in `pyproject`/tox to avoid sys.path hacks. Currently tests use `conftest.py` to inject `backend/` into `sys.path` — consider adding a proper package install step in CI (editable install) to avoid path manipulation.

2. Requirements and environments
- Split `requirements.txt` into `requirements.txt` (runtime) and `requirements-dev.txt` (pytest, test utilities). Avoid including heavy model dependencies in lightweight dev installs.

3. Separate concerns
- `app/` contains scoring, nlp_utils, feedback_llm, rubric_loader, config; consider grouping into `app/scoring/`, `app/embeddings/`, `app/feedback/` packages if the codebase grows.

4. Tests
- Add integration tests for frontend (using `requests` + a running backend) and end-to-end smoke tests in CI. Current tests cover the backend logic well.

5. CI
- Add matrix CI runs: (1) unit tests with fallback embeddings, (2) optional e2e with real `sentence-transformers` if the runner allows larger downloads.

6. Docs & examples
- Add `examples/` with sample transcripts and expected outputs.

7. Docker
- Add Compose file (already present) but add clear `docker-compose` instructions in README.

Small automated improvements I can apply now
- Split `backend/requirements.txt` into `requirements.txt` and `requirements-dev.txt` and update CI.
- Add an integration test (already added).

If you want, I can apply the automated improvements now (split requirements, adjust CI), or proceed with Phase 4 (LLM chain) next.
