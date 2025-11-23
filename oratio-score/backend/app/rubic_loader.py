# backend/app/rubric_loader.py
import pandas as pd
from typing import List, Dict
import os

RUBRIC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..", "data", "rubric.xlsx"
)
RUBRIC_PATH = os.path.abspath(RUBRIC_PATH)


def load_rubric(path: str | None = None) -> List[Dict]:
    p = path or RUBRIC_PATH
    # If the rubric file isn't present or is malformed, return a small default rubric
    if not os.path.exists(p):
        default = [
            {
                "name": "Content",
                "description": "Relevance and substance of the response.",
                "keywords": ["coding", "music", "sports", "projects"],
                "weight": 50.0,
                "min_words": 5,
                "max_words": None,
            },
            {
                "name": "Delivery",
                "description": "Clarity and fluency of delivery.",
                "keywords": ["confident", "clear", "engaging"],
                "weight": 50.0,
                "min_words": 0,
                "max_words": None,
            },
        ]
        return default

    df = pd.read_excel(p)
    # Minimal normalization
    required_cols = ["Criterion Name", "Description", "Keywords", "Weight"]
    for col in required_cols:
        if col not in df.columns:
            # Fallback to default rubric if file doesn't contain expected columns
            default = [
                {
                    "name": "Content",
                    "description": "Relevance and substance of the response.",
                    "keywords": ["coding", "music", "sports", "projects"],
                    "weight": 50.0,
                    "min_words": 5,
                    "max_words": None,
                },
                {
                    "name": "Delivery",
                    "description": "Clarity and fluency of delivery.",
                    "keywords": ["confident", "clear", "engaging"],
                    "weight": 50.0,
                    "min_words": 0,
                    "max_words": None,
                },
            ]
            return default

    rows = []
    for _, r in df.iterrows():
        keywords_cell = r.get("Keywords", "") or ""
        if isinstance(keywords_cell, str):
            keywords = [k.strip() for k in keywords_cell.split(",") if k.strip()]
        else:
            keywords = list(keywords_cell) if hasattr(keywords_cell, "__iter__") else []

        rows.append(
            {
                "name": r["Criterion Name"],
                "description": r["Description"],
                "keywords": keywords,
                "weight": float(r["Weight"]),
                "min_words": (
                    int(r.get("Min Words", 0))
                    if not pd.isna(r.get("Min Words", 0))
                    else None
                ),
                "max_words": (
                    int(r.get("Max Words", 0))
                    if not pd.isna(r.get("Max Words", 0))
                    else None
                ),
            }
        )
    return rows
