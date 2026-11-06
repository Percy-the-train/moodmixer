@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup first.
    pause
    exit /b 1
)
start "SER Server" ".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
timeout /t 4 /nobreak >nul
start "" http://127.0.0.1:8000
