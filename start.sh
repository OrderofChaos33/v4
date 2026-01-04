#!/bin/bash
# Quick start script for 280E MVP

set -e

echo "=================================="
echo "280E Expense Reclassification MVP"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

echo "Checking Python version..."
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "Error: Python 3.9 or higher is required. Found: $python_version"
    exit 1
fi
echo "✓ Python version OK: $python_version"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run tests
echo "Running tests..."
pytest tests/ -v --tb=short
echo ""

# Start server
echo "=================================="
echo "Starting FastAPI server..."
echo "=================================="
echo ""
echo "API will be available at:"
echo "  - Main API: http://localhost:8000"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
