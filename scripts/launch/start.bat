@echo off
REM Ultimate Tech Detection System - Start Script for Windows

echo 🚀 Starting Ultimate Tech Detection System...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  No .env file found!
    echo Please copy env.example to .env and configure your API keys
    pause
    exit /b 1
)

REM Start the server
echo 🌐 Starting server on http://localhost:9000
echo 📱 Dashboard: http://localhost:9000
echo 🔧 API: http://localhost:9000/api/
echo 🌐 External: http://159.65.65.140:9000
echo.
echo Press Ctrl+C to stop the server

python api_server.py
