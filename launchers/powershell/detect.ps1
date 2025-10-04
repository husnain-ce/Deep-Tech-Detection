# Tech Detection System - PowerShell Launcher
# Comprehensive web technology detection with organized datasets

Set-Location $PSScriptRoot\..

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Install requirements if needed
if (-not (Test-Path "venv\.installed")) {
    Write-Host "Installing requirements..."
    pip install -r ..\config\requirements.txt
    New-Item -Path "venv\.installed" -ItemType File
}

# Run the detection system with JSON output by default
python ..\main.py --output json $args
