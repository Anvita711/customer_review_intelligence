@echo off
echo ============================================================
echo   Customer Review Intelligence Platform - Setup
echo ============================================================

cd /d "%~dp0"

echo.
echo [1/4] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Installing frontend dependencies...
cd frontend
call npm install

echo.
echo [3/4] Building React frontend...
call npm run build
cd ..

echo.
echo [4/4] Running demo pipeline on sample data...
python demo_run.py

echo.
echo ============================================================
echo   Setup complete!
echo   Run start_server.bat to launch the full application.
echo ============================================================
pause
