import os
from typing import Optional


class Settings:
    # Embedding / model
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # scoring hyperparams
    KEYWORD_WEIGHT: float = float(os.getenv("KEYWORD_WEIGHT", "0.4"))
    SEMANTIC_WEIGHT: float = float(os.getenv("SEMANTIC_WEIGHT", "0.6"))
    LENGTH_PENALTY_UNDER_MIN: float = float(
        os.getenv("LENGTH_PENALTY_UNDER_MIN", "-10.0")
    )
    LENGTH_PENALTY_OVER_MAX: float = float(os.getenv("LENGTH_PENALTY_OVER_MAX", "-5.0"))

    # LLM config (optional)
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "300"))

    # API keys (optional)
    AZURE_OPENAI_KEY: Optional[str] = os.getenv("AZURE_OPENAI_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")


# single settings object to import elsewhere:
settings = Settings()
