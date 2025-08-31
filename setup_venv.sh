#!/bin/bash

# Setup script for Interview Coding Platform virtual environment

echo "Setting up virtual environment for Interview Coding Platform..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "orchestrator/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r orchestrator/requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install requirements"
        exit 1
    fi
else
    echo "Warning: requirements.txt not found, installing basic dependencies..."
    pip install fastapi uvicorn psutil pytest
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Interview Coding Platform Environment Variables
PYTHONPATH=./orchestrator
WORK_DIR=/tmp/code_execution
LOG_LEVEL=INFO
PERFORMANCE_MONITORING=true
CACHE_ENABLED=true
EOF
fi

echo "Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the performance demo:"
echo "  source venv/bin/activate && python orchestrator/simple_performance_demo.py"
echo ""
echo "To run tests:"
echo "  source venv/bin/activate && python -m pytest orchestrator/tests/"