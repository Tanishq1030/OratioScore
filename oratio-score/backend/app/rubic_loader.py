# backend/app/rubric_loader.py
import pandas as pd
from typing import List, Dict, Optional
import os
import re

RUBRIC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..", "data", "rubric.xlsx"
)
RUBRIC_PATH = os.path.abspath(RUBRIC_PATH)


def _default_rubric() -> List[Dict]:
    return [
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


def _normalize(s: Optional[str]) -> str:
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def _normalize_column_name(col: str) -> str:
    s = _normalize(col)
    if "criterion" in s:
        return "Criterion Name"
    if "description" in s:
        return "Description"
    if "keyword" in s:
        return "Keywords"
    if "weight" in s:
        return "Weight"
    if "min" in s and "word" in s:
        return "Min Words"
    if "max" in s and "word" in s:
        return "Max Words"
    return col


def load_rubric(path: Optional[str] = None) -> List[Dict]:
    p = path or RUBRIC_PATH
    if not os.path.exists(p):
        return _default_rubric()

    # First try reading with header=0
    try:
        df = pd.read_excel(p, header=0)
    except Exception:
        return _default_rubric()

    required_cols = {"Criterion Name", "Description", "Keywords", "Weight"}
    df_cols = set(map(str, df.columns))
    if not required_cols.issubset(df_cols):
        # Attempt to auto-detect header row by scanning first 10 rows
        try:
            raw = pd.read_excel(p, header=None, dtype=str)
        except Exception:
            return _default_rubric()

        header_row: Optional[int] = None
        scan_rows = min(10, len(raw))
        for i in range(scan_rows):
            row_vals = [str(x) for x in raw.iloc[i].fillna("").values]
            norms = [_normalize(v) for v in row_vals]
            hits = 0
            if any("criterion" in v for v in norms):
                hits += 1
            if any("keyword" in v for v in norms):
                hits += 1
            if any("description" in v for v in norms):
                hits += 1
            if any("weight" in v for v in norms):
                hits += 1
            if hits >= 2:
                header_row = i
                break

        if header_row is None:
            return _default_rubric()

        try:
            df = pd.read_excel(p, header=header_row)
        except Exception:
            return _default_rubric()

    # Normalize column names to canonical ones where possible
    rename_map = {c: _normalize_column_name(c) for c in df.columns}
    df = df.rename(columns=rename_map)

    # Ensure required columns are present after rename
    if not required_cols.issubset(set(map(str, df.columns))):
        return _default_rubric()

    rows: List[Dict] = []
    for _, r in df.iterrows():
        keywords_cell = r.get("Keywords", "") or ""
        if isinstance(keywords_cell, str):
            keywords = [k.strip() for k in keywords_cell.split(",") if k.strip()]
        else:
            keywords = list(keywords_cell) if hasattr(keywords_cell, "__iter__") else []

        rows.append(
            {
                "name": r.get("Criterion Name"),
                "description": r.get("Description", ""),
                "keywords": keywords,
                "weight": float(r.get("Weight", 0) or 0.0),
                "min_words": (
                    int(r.get("Min Words", 0))
                    if ("Min Words" in r and not pd.isna(r.get("Min Words", 0)))
                    else None
                ),
                "max_words": (
                    int(r.get("Max Words", 0))
                    if ("Max Words" in r and not pd.isna(r.get("Max Words", 0)))
                    else None
                ),
            }
        )

    return rows
