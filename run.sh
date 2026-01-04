#!/bin/bash
# Simple startup script for 280E Classification Tool

echo "Starting 280E Expense Classification Tool..."
echo ""
echo "Make sure you have installed dependencies:"
echo "  pip install -r requirements.txt"
echo ""
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
