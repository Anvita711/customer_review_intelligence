@echo off
echo ============================================================
echo   Development Mode (hot-reload frontend + backend)
echo ============================================================
echo.
echo   Backend API:   http://localhost:8000
echo   Frontend Dev:  http://localhost:3000  (proxies /api to :8000)
echo.
echo   Starting backend...
cd /d "%~dp0"
start "API Server" cmd /k "python run_server.py --reload"

echo   Starting frontend dev server...
cd frontend
start "React Dev" cmd /k "npm run dev"

echo.
echo   Both servers are starting in separate windows.
echo ============================================================
