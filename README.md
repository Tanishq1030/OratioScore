# OratioScore — Final README

OratioScore is an AI-powered transcript scoring tool built for the Nirmaan AI Intern Case Study. It combines deterministic rule-based scoring (keywords + length penalties), semantic similarity (sentence-transformers embeddings), rubric weighting, and optional LLM-based textual feedback. The project includes a FastAPI backend and a Streamlit frontend.

---

Table of contents

- About
- Repo layout
- Requirements
- Quick start — run locally
- Backend (development)
- Frontend (development)
- Run tests
- Optional: Docker (local dev)
- API — endpoints & examples
- Configuration / environment variables
- ZON support
- Deployment recommendations
- Troubleshooting & tips
- Contact / credits

---

About

OratioScore ingests a transcript and returns:

- `overall_score` (0–100)
- Per-criterion scores, with keyword and semantic breakdown
- Rule-based length penalties and weighting logic
- Structured `evidence` suitable for LLM feedback
- Optional LLM-generated textual feedback (LangChain + OpenAI/Azure), with deterministic fallback

Designed to be reproducible, testable, and easy to deploy.

---

Repo layout (important files)

```
oratio-score/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py
│   │   ├── scoring.py
│   │   ├── nlp_utils.py
│   │   ├── rubric_loader.py
│   │   ├── feedback_llm.py
│   │   ├── zon.py             # ZON serializer + parser
│   │   └── __init__.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── streamlit_app.py
│   └── requirements.txt
├── data/
│   └── rubric.xlsx
├── docs/
│   └── scoring_formula.md
├── scripts/
│   └── (convenience and cleanup scripts)
├── tests/
│   └── (pytest test files)
└── README.md
```

---

Requirements

- Python 3.10+ (3.11 recommended)
- `pip` and virtualenv support
- Optional: Docker & docker-compose (if you plan to use containers)
- Internet access for first-time transformer download (sentence-transformers)

Key Python libraries (installed by `requirements.txt`):

- fastapi, uvicorn
- pandas, openpyxl, numpy
- sentence-transformers
- streamlit
- langchain, openai (optional; for LLM feedback)
- pytest

---

Quick start — Run locally

Follow these steps exactly. Commands assume you are at the repository root (`oratio-score/`). Use Git Bash, WSL, or a Unix-like shell on Windows for best compatibility.

Note: First run may download a transformer model (~50–150 MB). Be patient.

## Makefile — Usage & Instructions

This repository includes a top-level `Makefile` to simplify common development tasks (create venv, run backend, run frontend, run tests, and convenient dev mode). Place the `Makefile` at the repository root (`oratio-score/Makefile`). Run the `make` targets from the repo root.

> **File name:** `Makefile` (no extension)

---

### Available targets

- `make venv`  
  Create a local virtual environment at `./.venv` (if missing) and install backend and frontend dependencies.

- `make run-backend`  
  Start the FastAPI backend from the repository root (uses the ASGI entrypoint `asgi:app`):  
  ```bash
  uvicorn asgi:app --reload --port 8000


1) Create and activate a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows (cmd.exe)

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Using Conda (Recommended on Windows)

```bash
conda create -n oratioscore python=3.10 -y
conda activate oratioscore


2) Install backend requirements

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

If you plan to use the LLM feedback layer, make sure the optional LLM packages in `requirements.txt` are installed and that you provide API keys via environment variables.

3) Place the rubric file

Ensure the rubric Excel is present at `data/rubric.xlsx` (or `backend/data/rubric.xlsx` depending on your layout). Expected columns (case-insensitive):

- Criterion Name
- Description
- Keywords (comma-separated)
- Weight
- Min Words (optional)
- Max Words (optional)

4) Run the backend (development)

If you usually start services from the repository root, use the provided ASGI entrypoint:

From repo root:

```bash
uvicorn asgi:app --reload --port 8000
```

Alternatively, to run directly from the `backend/` folder (no wrapper file required):

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Health: `http://127.0.0.1:8000/health` — returns `{"status":"ok"}`
API docs (Swagger): `http://127.0.0.1:8000/docs`

5) Install frontend dependencies and run Streamlit

Open a new terminal (repo root) and reuse the same venv:

```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit runs on `http://localhost:8501` by default. The Streamlit app uses `http://localhost:8000` as the backend unless you set `ORATIO_BACKEND_URL` via environment or Streamlit secrets.

6) Example: score via curl

```bash
curl -X POST "http://127.0.0.1:8000/score" \
   -H "Content-Type: application/json" \
   -d '{"text":"Hello, I am Tan. I like coding and music."}'
```

7) Running tests

From repo root:

```bash
pytest -q
```

If `ModuleNotFoundError` arises, run tests with `PYTHONPATH=backend pytest -q` or ensure tests/conftest.py adds `backend` to `sys.path` (the repo includes `conftest.py`).

---

Optional: Docker (local dev)

Docker is optional. There are Dockerfiles for the backend and frontend and a `docker-compose.yml` for local development.

Quick compose (from repo root):

```bash
docker compose up --build
```

Notes:
- The frontend is configured to talk to the backend via the Compose service name `http://backend:8000`.
- Model downloads can be memory- and time-consuming; prefer to run the backend outside Docker on low-memory machines.

---

API — Endpoints & payloads

POST `/score`

Input (JSON):

```json
{ "text": "Transcript text here..." }
```

Response (JSON):

```json
{
   "overall_score": 72.4,
   "word_count": 134,
   "criteria": [
      {
         "name": "Clarity",
         "weight": 10,
         "keyword_score": 78.0,
         "keywords_found": ["family","hobbies"],
         "semantic_score": 82.0,
         "length_penalty": 0,
         "raw_score": 78.8,
         "weighted_score": 7.88
      }
   ],
   "evidence": { "Clarity": { /* ... */ } },
   "feedback": { /* optional LLM feedback */ }
}
```

ZON support: API accepts/returns JSON by default. If `Content-Type` or `Accept` is set to `application/zon` or `text/zon`, the backend will attempt to parse/serialize ZON when the parser is implemented and enabled. By default, downloads can be produced in ZON (serializer present).

---

Configuration / environment variables

Place these in your shell or a `.env` (don’t commit secrets):

```
# backend/app/config.py reads these
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
KEYWORD_WEIGHT=0.4
SEMANTIC_WEIGHT=0.6
LENGTH_PENALTY_UNDER_MIN=-10.0
LENGTH_PENALTY_OVER_MAX=-5.0

# Optional LLM keys for textual feedback
OPENAI_API_KEY=sk-...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=deployment-name
```

In Streamlit Cloud, add `BACKEND_URL` in the secrets panel:

```
BACKEND_URL="https://your-backend-url"
```

---

ZON (ZeroTier Object Notation) support

The repo includes a conservative ZON serializer (`backend/app/zon.py`) that can write human-friendly ZON files. A tolerant parser is available and the backend supports content negotiation for ZON when enabled. By design, ZON is additive — JSON remains the default API contract.

---

Deployment recommendations (public hosting)

Frontend: Streamlit Cloud (free tier)

Connect GitHub repo, set the main file to `frontend/streamlit_app.py` and add the `BACKEND_URL` secret.

Backend: Render (Web Service) or Railway

Build command: `pip install -r backend/requirements.txt`
Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Add environment variables (`OPENAI_API_KEY`, `EMBEDDING_MODEL`, etc.) in the hosting dashboard.

---

Troubleshooting & tips

- Model download slow or out of memory: run locally on a larger machine, or pre-download the model on a machine with sufficient RAM. For CI, mock or stub `get_embedding` to avoid large downloads.
- Tests failing with import errors: ensure `PYTHONPATH=backend` or that `tests/conftest.py` is present — it is included to add `backend/` to `sys.path`.
- Docker build fails: prefer runtime deploy (Render) for submission. Keep Dockerfiles for documentation; rework compose build contexts if needed.
- Streamlit can’t reach backend: confirm `ORATIO_BACKEND_URL` and that CORS is enabled in `backend/app/main.py` (it is by default).

---

Contact / credits

Author: You (prepared for the Nirmaan AI Intern Case Study)

Built with: FastAPI, Streamlit, Sentence-Transformers, LangChain (optional), Pandas, NumPy

Final notes

For the case submission: deploy backend to Render and frontend to Streamlit Cloud. This yields public URLs you can include in your submission. Keep Dockerfiles in the repo as documentation of production readiness, but do not rely on them for a first-time deployment to meet a deadline.

## Docker (recommended for contributors)

You can run the whole project (backend + frontend) with Docker Compose. The repository contains a `docker-compose.yml` that builds the `backend` and `frontend` services from their respective folders. This is the easiest way for contributors to get started without installing Python dependencies locally.

Quick start (Unix/macOS):

```bash
# from repo root
docker compose up --build
```

Quick start (Windows PowerShell / CMD):

```powershell
# from repo root
docker compose up --build
```

Convenience scripts

Two convenience scripts are provided to make this even easier:

- `scripts/dev-docker-up.sh` — a small shell script for Unix-like systems that runs `docker compose up --build` from the repo root.
- `scripts\dev-docker-up.bat` — a Windows batch script that does the same from a CMD prompt.

Notes
- The frontend service is configured to talk to the backend service via the Compose service name `http://backend:8000`.
- If you need to override the backend URL (only for advanced debugging), set the `ORATIO_BACKEND_URL` environment variable for the `frontend` service in `docker-compose.yml`.

Stopping

```bash
docker compose down
```
