# backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional


class ScoreRequest(BaseModel):
    text: str


class CriterionScore(BaseModel):
    name: str
    keyword_score: float
    keywords_found: List[str]
    semantic_score: float
    length_penalty: float
    raw_score: float
    weighted_score: float


class ScoreResponse(BaseModel):
    overall_score: Optional[float]
    word_count: int
    criteria: List[CriterionScore]
