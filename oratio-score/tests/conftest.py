# tests/conftest.py
import sys
from pathlib import Path

# repo_root/tests/conftest.py -> repo_root
REPO_ROOT = Path(__file__).resolve().parents[1]

# path to backend folder that contains `app/`
BACKEND_PATH = REPO_ROOT / "backend"

# Prepend backend to sys.path so tests can import `app.*`
sys.path.insert(0, str(BACKEND_PATH))
