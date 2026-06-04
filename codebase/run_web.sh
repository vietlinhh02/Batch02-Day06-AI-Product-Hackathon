#!/bin/bash
# Run Web UI for testing RAG pipeline
# Usage: ./run_web.sh

cd "$(dirname "$0")"

echo "=========================================="
echo "   CLASSBOT - WEB TEST UI"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "[1] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[2] Activating venv..."
source venv/bin/activate

echo "[3] Installing dependencies..."
pip install -q -r requirements.txt flask

echo "[4] Starting web server..."
echo ""
echo "    Open browser: http://localhost:5000"
echo "    Press Ctrl+C to stop"
echo ""
python3 web_ui.py
