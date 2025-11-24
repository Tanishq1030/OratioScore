# Phase 5 — Deployment (Backend + Frontend)

## Overview
Phase 5 deploys the full stack publicly using free-tier services.

---

## Objectives
- Deploy backend (FastAPI).
- Deploy frontend (Streamlit).
- Configure environment variables.
- Ensure system works end-to-end on public URL.

---

## Deployment Options

### Backend — Render (recommended)
1. Create new Web Service.
2. Set build command:
```bash
pip install -r backend/requirements.txt
```

3. Start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. Add environment variables:
- BACKEND_URL=
- AZURE_OPENAI_KEY=
- OPENAI_API_KEY=

### Frontend — Streamlit Cloud
1. Connect GitHub repo.
2. Add `.streamlit/secrets.toml`:
```toml
BACKEND_URL="https://your-backend.onrender.com"
```
3. Set main file to `frontend/streamlit_app.py` and deploy.

## Phase Completion Criteria
- Both services are publicly accessible.
- Frontend successfully calls `/score`.
