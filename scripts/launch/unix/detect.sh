#!/bin/bash
# Tech Detection System - Unix/macOS Launcher
# Comprehensive web technology detection with organized datasets

cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing requirements..."
    pip install -r ../config/requirements.txt
    touch venv/.installed
fi

# Run the detection system with JSON output by default
python ../main.py --output json "$@"
