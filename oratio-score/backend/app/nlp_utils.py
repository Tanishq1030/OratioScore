# backend/app/nlp_utils.py
import re
from typing import List


def clean_text(text: str) -> str:
    if not text:
        return ""
    # Basic cleaning: normalize whitespace, remove repeated spaces
    t = text.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def tokenize_words(text: str) -> List[str]:
    text = clean_text(text).lower()
    # simple word tokenizer
    words = re.findall(r"\b\w+\b", text)
    return words


def count_words(text: str) -> int:
    return len(tokenize_words(text))


def find_keywords(text: str, keywords: List[str]) -> List[str]:
    text_lower = clean_text(text).lower()
    found = []
    for kw in keywords:
        if not kw:
            continue
        if kw.lower() in text_lower:
            found.append(kw)
    return found
