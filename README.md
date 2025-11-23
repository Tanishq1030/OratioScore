# OratioScore (Phase 1) — Skeleton

**Status:** Phase 1 complete — repo skeleton, basic API endpoints, simple Streamlit frontend (skeleton scoring).

This repository implements Phase 1 of the Nirmaan AI intern case study:

- Skeleton FastAPI backend with `/health` and `/score` endpoints.
- Basic rubric loader stub that expects `data/rubric.xlsx`.
- Minimal NLP utilities and scoring function placeholders.
- Streamlit frontend that calls the backend.
- Phase 2 will add embeddings, deterministic scoring, and LLM feedback.

## Local quickstart (dev)

1. Ensure `data/rubric.xlsx` exists (place the provided rubric in `data/`).
2. Create virtualenv & install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
