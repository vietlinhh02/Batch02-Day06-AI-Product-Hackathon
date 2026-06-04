#!/bin/bash
# Run RAG test in CLI mode
# Usage: ./run_test.sh

cd "$(dirname "$0")"

echo "=========================================="
echo "   CLASSBOT - RAG PIPELINE TEST"
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
pip install -q -r requirements.txt

echo "[4] Running RAG test..."
python3 test_rag.py
