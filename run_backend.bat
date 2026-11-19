@echo off
setlocal
echo =====================================================================
echo  Starting Research Scope Backend (FastAPI + Uvicorn)
echo =====================================================================
cd /d "%~dp0backend" || exit /b 1

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
)

pause
