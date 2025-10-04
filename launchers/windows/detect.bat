@echo off
REM Tech Detection System - Windows Launcher
REM Comprehensive web technology detection with organized datasets

cd /d "%~dp0\.."

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
if not exist "venv\.installed" (
    echo Installing requirements...
    pip install -r ..\config\requirements.txt
    echo. > venv\.installed
)

REM Run the detection system with JSON output by default
python ..\main.py --output json %*
