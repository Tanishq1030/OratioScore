# backend/app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Any, Dict

from app import config
from app.scoring import score_transcript as scoring_pipeline
from app.zon import zon_parse, zon_serialize
import json


app = FastAPI(title="OratioScore - Backend")

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
async def score_transcript(request: Request):
    """Run the deterministic scoring pipeline and return JSON or ZON response.

    Accepts:
      - JSON body: {"text": "..."}
      - ZON body: text "..."  OR { text "..." }

    Returns JSON by default. If `Accept` header includes 'zon', returns ZON.
    """
    content_type = request.headers.get("content-type", "").lower()
    accept = request.headers.get("accept", "").lower()

    # parse input
    text_val = None
    raw_body = await request.body()
    body_text = raw_body.decode("utf-8") if raw_body else ""

    try:
        if "zon" in content_type:
            parsed = zon_parse(body_text)
            # allow top-level 'text' key or bare string under 'text'
            text_val = parsed.get("text") if isinstance(parsed, dict) else None
        else:
            # default JSON parsing
            data = await request.json()
            text_val = data.get("text")
    except Exception:
        return Response(status_code=400, content="Invalid request format")

    if not text_val or not str(text_val).strip():
        payload = {
            "overall_score": 0.0,
            "word_count": 0,
            "criteria": [],
            "evidence": {},
            "error": "No transcript provided",
        }
        if "zon" in accept:
            return Response(
                content=zon_serialize(payload), media_type="application/zon"
            )
        return payload

    try:
        res = scoring_pipeline(str(text_val))
        # return ZON if requested
        if "zon" in accept:
            return Response(content=zon_serialize(res), media_type="application/zon")
        return res
    except Exception as e:
        payload = {
            "overall_score": 0.0,
            "word_count": len(str(text_val).split()),
            "criteria": [],
            "evidence": {},
            "error": "Scoring failed",
            "details": str(e),
        }
        if "zon" in accept:
            return Response(
                content=zon_serialize(payload), media_type="application/zon"
            )
        return payload


@app.get("/", include_in_schema=False)
def root():
    # redirect root to the interactive docs
    return RedirectResponse(url="/docs")
