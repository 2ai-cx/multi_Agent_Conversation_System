#!/bin/bash

# 🧪 Local Testing Quick Start Script
# Run this to test the multi-agent system locally

set -e  # Exit on error

echo "🚀 Multi-Agent System - Local Testing"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Choose a test option:"
echo "  1) Run unit tests"
echo "  2) Run integration tests (requires Temporal)"
echo "  3) Start server for manual testing"
echo "  4) Run all tests with coverage"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🧪 Running unit tests..."
        pytest tests/unit/ -v
        ;;
    2)
        echo ""
        echo "🔍 Checking if Temporal is running..."
        if ! curl -s http://localhost:8233 > /dev/null; then
            echo "❌ Temporal is not running!"
            echo "Start it with: temporal server start-dev"
            exit 1
        fi
        echo "✅ Temporal is running"
        echo ""
        echo "🧪 Running integration tests..."
        pytest tests/integration/ -v
        ;;
    3)
        echo ""
        echo "🔍 Checking if Temporal is running..."
        if ! curl -s http://localhost:8233 > /dev/null; then
            echo "⚠️  Temporal is not running!"
            echo "Start it in another terminal with: temporal server start-dev"
            echo ""
            read -p "Continue anyway? (y/n): " continue
            if [ "$continue" != "y" ]; then
                exit 1
            fi
        else
            echo "✅ Temporal is running"
        fi
        echo ""
        echo "🚀 Starting server on http://localhost:8003..."
        echo "Press Ctrl+C to stop"
        echo ""
        python unified_server.py
        ;;
    4)
        echo ""
        echo "🧪 Running all tests with coverage..."
        pytest tests/ --cov=agents --cov-report=html --cov-report=term-missing
        echo ""
        echo "📊 Coverage report generated in htmlcov/index.html"
        echo "Open it with: open htmlcov/index.html"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
