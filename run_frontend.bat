@echo off
setlocal
echo =====================================================================
echo  Starting Research Scope Frontend (Vite + React)
echo =====================================================================
cd /d "%~dp0frontend" || exit /b 1

call npm run dev

pause
