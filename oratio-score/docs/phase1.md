# Phase 1 — Project Foundation & Skeleton

## Overview
Phase 1 establishes the foundational structure for the OratioScore project. It provides a clean, production-ready layout for the backend, frontend, tests, and documentation. This phase ensures that all subsequent phases can be built incrementally without refactoring.

---

## Objectives
- Create initial backend and frontend scaffolding.
- Add project-wide documentation.
- Prepare test infrastructure.
- Establish clean developer experience with health checks and routing.

---

## Deliverables

### 1. Backend (FastAPI)
- `GET /health` endpoint for uptime checks.
- `GET /` redirect to `/docs` for developer convenience.
- `POST /score` endpoint stub (placeholder).
- Project modules created:
  - `main.py`
  - `config.py`
  - `nlp_utils.py` (stub)
  - `rubric_loader.py` (stub)
  - `scoring.py` (stub)
  - `feedback_llm.py` (stub)
  - `schemas.py`

### 2. Frontend (Streamlit)
- Basic transcript textbox.
- Button to trigger scoring.
- Minimal placeholder results section.
- Backend URL configurable via secrets.

### 3. Documentation
- Initial README.
- Initial scoring_formula.md.
- Deployment instructions scaffold.
- Demo script scaffold.

### 4. Tests
- `tests/` folder added.
- Basic `test_scoring.py` ensuring backend imports cleanly.
- Introduced `conftest.py` to manage import paths.

### 5. Dev Tools
- `docker-compose.yml` added.
- `backend/requirements.txt` added.

---

## Phase Completion Criteria
- Backend runs via `uvicorn` without import errors.
- Streamlit frontend renders successfully.
- Placeholder `/score` endpoint accepts text input.
- Tests execute without failures (for Phase 1 scope).
