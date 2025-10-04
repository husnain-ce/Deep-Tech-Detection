@echo off
REM Ultimate Web Technology Detection System Launcher

echo 🚀 Ultimate Web Technology Detection System
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed
    exit /b 1
)

REM Run the detector
python main.py %*
