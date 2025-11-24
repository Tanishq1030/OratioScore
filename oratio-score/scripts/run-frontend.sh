#!/usr/bin/env bash
# scripts/run-frontend.sh
set -euo pipefail

# Usage:
# ./scripts/run-frontend.sh [BACKEND_URL]
# Example:
# ./scripts/run-frontend.sh http://127.0.0.1:8000

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/.venv"

# Optional backend URL from arg or environment
BACKEND_URL="${1:-${BACKEND_URL:-http://127.0.0.1:8000}}"

echo "Root: $ROOT_DIR"
echo "Frontend dir: $FRONTEND_DIR"
echo "Using BACKEND_URL: $BACKEND_URL"

# Activate venv if it exists
if [ -d "$VENV_DIR" ]; then
  echo "Activating virtualenv at $VENV_DIR"
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
else
  echo "No virtualenv found at $VENV_DIR — continuing with current Python environment."
fi

# Ensure frontend deps installed
echo "Installing frontend requirements (if needed)..."
pip install -r "$FRONTEND_DIR/requirements.txt"

# Export BACKEND_URL for Streamlit
export BACKEND_URL="$BACKEND_URL"

# Start Streamlit
echo "Starting Streamlit..."
cd "$FRONTEND_DIR"
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
