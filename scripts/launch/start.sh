#!/bin/bash
# Ultimate Tech Detection System - Start Script

echo "🚀 Starting Ultimate Tech Detection System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please copy env.example to .env and configure your API keys"
    exit 1
fi

# Start the server
echo "🌐 Starting server on http://localhost:9000"
echo "📱 Dashboard: http://localhost:9000"
echo "🔧 API: http://localhost:9000/api/"
echo "🌐 External: http://159.65.65.140:9000"
echo ""
echo "Press Ctrl+C to stop the server"

python3 api_server.py
