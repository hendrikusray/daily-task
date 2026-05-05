#!/bin/bash

# CMS Application Launcher Script

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/update dependencies if needed
echo "Checking dependencies..."
pip install -r requirements.txt --quiet

# Run application
echo ""
echo "=========================================="
echo "🚀 Starting CMS Application..."
echo "=========================================="
echo ""
echo "📱 Open your browser:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

cd app
python app.py
