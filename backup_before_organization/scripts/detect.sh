#!/bin/bash
# Ultimate Web Technology Detection System Launcher

echo "🚀 Ultimate Web Technology Detection System"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Run the detector
python3 main.py "$@"
