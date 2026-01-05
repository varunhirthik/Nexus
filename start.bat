@echo off
echo ============================================================
echo   Live News Analyst - Automated Startup Script
echo ============================================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file from .env.example:
    echo   1. copy .env.example .env
    echo   2. Edit .env and add your GEMINI_API_KEY
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

echo [INFO] Installing Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if not exist frontend\node_modules (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo ============================================================
echo   Starting Services
echo ============================================================
echo.

REM Start backend in new window
echo [INFO] Starting backend server...
start "Live News Analyst - Backend" cmd /k "venv\Scripts\activate && python src\main.py"

REM Wait a bit for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend in new window
echo [INFO] Starting frontend dev server...
start "Live News Analyst - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo   Services Started!
echo ============================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in each window to stop the services
echo.
pause
