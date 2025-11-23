# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Any, Dict

from app import config

app = FastAPI(title="OratioScore - Backend (Phase 1)")

# Allow local dev from Streamlit or other hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreRequest(BaseModel):
    text: str


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "app": "oratio-score-backend"}


@app.post("/score")
def score_transcript(req: ScoreRequest):
    """
    Phase 1 placeholder:
    - Validates input and returns a skeleton response object.
    - The real scoring pipeline will be implemented in Phase 2.
    """
    text_len = len(req.text or "")
    words = len((req.text or "").split())
    return {
        "overall_score": None,
        "message": "Scoring engine not implemented yet. Phase 1 skeleton active.",
        "word_count": words,
        "char_count": text_len,
        "criteria": [],
    }


@app.get("/", include_in_schema=False)
def root():
    # redirect root to the interactive docs
    return RedirectResponse(url="/docs")
