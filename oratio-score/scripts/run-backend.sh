#!/bin/bash
echo "Starting OratioScore backend..."

# check for uvicorn
if ! command -v uvicorn >/dev/null 2>&1; then
	echo "Error: 'uvicorn' not found in PATH."
	echo "Install it into your active virtualenv with: pip install uvicorn[standard]" >&2
	exit 1
fi

uvicorn asgi:app --reload --port 8000
