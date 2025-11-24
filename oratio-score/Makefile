# Makefile — OratioScore helper targets
# Usage:
#   make venv              # create virtualenv and install deps
#   make run-backend       # start backend (FastAPI)
#   make run-frontend      # start frontend (Streamlit)
#   make test              # run pytest
#   make dev               # start backend in background + frontend in foreground (UNIX)
#   make stop-dev          # stop background backend started by `make dev` (UNIX)

PY := python
PIP := $(PY) -m pip
UVICORN := uvicorn
STREAMLIT := streamlit
PYTEST := pytest

# Ports
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 8501

# Backend start command (from repo root)
# Use the ASGI entrypoint so repo-root invocation works consistently
BACKEND_CMD := $(UVICORN) asgi:app --reload --port $(BACKEND_PORT)

# Frontend start command
FRONTEND_CMD := $(STREAMLIT) run frontend/streamlit_app.py --server.port $(FRONTEND_PORT) --server.address 0.0.0.0

# Virtualenv .venv at repo root (optional)
VENV_DIR := .venv
VENV_PY := $(VENV_DIR)/Scripts/python.exe

.PHONY: venv run-backend run-frontend test dev stop-dev

venv:
	@echo "Creating virtualenv (if missing) and installing deps..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PY) -m venv $(VENV_DIR); \
		echo "Virtualenv created at $(VENV_DIR)"; \
	else \
		echo "Virtualenv exists at $(VENV_DIR)"; \
	fi
	@echo "Activating virtualenv and installing backend/frontend dependencies..."
	# Install backend deps
	$(VENV_DIR)/bin/python -m pip install --upgrade pip || $(PY) -m pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r backend/requirements.txt || $(PIP) install -r backend/requirements.txt
	# Install frontend deps
	$(VENV_DIR)/bin/pip install -r frontend/requirements.txt || $(PIP) install -r frontend/requirements.txt
	@echo "Done."

# Run backend from repo root (uses asgi.py to place backend on sys.path)
run-backend:
	@echo "Starting backend on port $(BACKEND_PORT)..."
	$(BACKEND_CMD)

# Run frontend (Streamlit)
run-frontend:
	@echo "Starting frontend (Streamlit) on port $(FRONTEND_PORT)..."
	$(FRONTEND_CMD)

# Run tests (ensures backend is importable)
test:
	@echo "Running tests (pytest)..."
	# Ensure backend path is available to test runner
	PYTHONPATH=backend $(PY) -m $(PYTEST) -q

# Development convenience: start backend in background then start frontend (UNIX only)
dev:
	@echo "Starting backend in background and frontend in foreground (UNIX only)."
	# start backend in background and save pid
	PYTHONPATH=backend nohup $(BACKEND_CMD) > backend_dev.log 2>&1 & echo $$! > dev_backend.pid
	# give backend a moment to start
	sleep 1
	$(FRONTEND_CMD)

# Stop background backend launched by `make dev`
stop-dev:
	@if [ -f dev_backend.pid ]; then \
		pid=$$(cat dev_backend.pid); \
		echo "Stopping backend (pid $$pid)"; \
		kill $$pid || echo "kill failed; you may need to stop it manually"; \
		rm -f dev_backend.pid; \
	else \
		echo "No dev_backend.pid found; nothing to stop."; \
	fi
