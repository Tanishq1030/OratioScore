@echo off
echo Starting OratioScore backend...

where uvicorn >nul 2>&1
if errorlevel 1 (
	echo Error: 'uvicorn' not found on PATH.
	echo Install it into your active virtualenv with: pip install uvicorn[standard]
	exit /b 1
)

uvicorn asgi:app --reload --port 8000
