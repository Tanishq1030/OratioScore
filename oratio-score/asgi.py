"""ASGI entrypoint for running the backend from the repository root.

This file ensures the `backend` package directory is on `sys.path` so you can run:

  uvicorn asgi:app --reload --port 8000

from the repo root (`oratio-score/`).
"""

import os
import sys

HERE = os.path.dirname(__file__)
BACKEND_PATH = os.path.join(HERE, "backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

# Import the FastAPI 'app' instance from backend.app.main
from app.main import app  # noqa: E402
