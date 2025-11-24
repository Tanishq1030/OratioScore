:: scripts\run-frontend.bat
@echo off
REM Usage: run-frontend.bat [BACKEND_URL]
SET ROOT=%~dp0\..
SET FRONTEND_DIR=%ROOT%\frontend
SET VENV_ACT=%ROOT%\.venv\Scripts\activate.bat
SET BACKEND_URL=%1

IF "%BACKEND_URL%"=="" (
  IF DEFINED BACKEND_URL (
    SET BACKEND_URL=%BACKEND_URL%
  ) ELSE (
    SET BACKEND_URL=http://127.0.0.1:8000
  )
)

ECHO Root: %ROOT%
ECHO Frontend dir: %FRONTEND_DIR%
ECHO Using BACKEND_URL: %BACKEND_URL%

IF EXIST "%VENV_ACT%" (
  ECHO Activating virtualenv...
  CALL "%VENV_ACT%"
) ELSE (
  ECHO No virtualenv found at %VENV_ACT% - using current Python environment.
)

ECHO Installing frontend requirements (if needed)...
pip install -r "%FRONTEND_DIR%\requirements.txt"

ECHO Setting BACKEND_URL env for this session...
SET BACKEND_URL=%BACKEND_URL%

CD /D "%FRONTEND_DIR%"
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
