# Deployment Instructions

## Backend (FastAPI) — Render

1. Push repo to GitHub.
2. Create a new Render Web Service.
3. Set:
   - **Runtime:** Python
   - **Build Command:**
     ```
     pip install -r backend/requirements.txt
     ```
   - **Start Command:**
     ```
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
4. Add environment variables:
   - `OPENAI_API_KEY` (optional)
   - `AZURE_OPENAI_KEY` (optional)
   - `EMBEDDING_ALLOW_FALLBACK` (set `0` to force errors if sentence-transformers missing)

5. Deploy.

---

## Frontend (Streamlit) — Streamlit Cloud

1. Connect GitHub repository.
2. Create `.streamlit/secrets.toml`:
```toml
BACKEND_URL="https://your-backend.onrender.com"
```
3. Set main file as `frontend/streamlit_app.py`.

Deploy.

### Testing Deployment

1. Visit Streamlit URL.
2. Paste transcript.
3. Ensure results appear.
