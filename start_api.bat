@echo off
echo Starting Review Intelligence API on http://localhost:8000
echo Swagger docs at http://localhost:8000/docs
echo.
echo TIP: Use start_server.bat to serve both API and frontend together.
echo.
cd /d "%~dp0"
python run_server.py --reload
