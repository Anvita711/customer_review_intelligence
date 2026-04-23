@echo off
echo ============================================================
echo   Customer Review Intelligence Platform
echo ============================================================
echo.

cd /d "%~dp0"

:: Check if frontend build exists
if not exist "frontend\dist\index.html" (
    echo [!] Frontend not built yet. Building now...
    cd frontend
    call npm install
    call npm run build
    cd ..
    echo.
)

echo   API + Frontend:  http://localhost:8000
echo   Swagger Docs:    http://localhost:8000/docs
echo   Press Ctrl+C to stop.
echo.
echo ============================================================

python run_server.py --reload
