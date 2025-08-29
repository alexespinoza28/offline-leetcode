#!/bin/bash
set -e

echo "=== Interview Coding Platform - Docker Container Starting ==="
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "Working Directory: $(pwd)"
echo "Python Path: $PYTHONPATH"

# Create necessary directories
mkdir -p /app/logs /app/data /app/problems /app/templates

# Set up logging
touch /app/logs/orchestrator.log /app/logs/frontend.log /app/logs/supervisord.log
chmod 644 /app/logs/*.log

# Verify Python environment
echo "=== Python Environment ==="
python3 --version
pip --version
echo "Python path: $(which python3)"

# Verify Node.js environment  
echo "=== Node.js Environment ==="
node --version
npm --version
echo "Node path: $(which node)"

# Verify language compilers
echo "=== Language Compilers ==="
gcc --version | head -1
g++ --version | head -1
java -version 2>&1 | head -1

# Check database
echo "=== Database Setup ==="
if [ -f "/app/data/interview_platform.db" ]; then
    echo "Database exists: /app/data/interview_platform.db"
    sqlite3 /app/data/interview_platform.db ".tables" || echo "Database tables check failed"
else
    echo "Database not found, will be created on first orchestrator start"
fi

# Check orchestrator dependencies
echo "=== Orchestrator Dependencies ==="
cd /app/orchestrator
python3 -c "
try:
    import fastapi, uvicorn, sqlite3, json, pathlib
    print('✓ Core dependencies available')
except ImportError as e:
    print(f'✗ Missing dependency: {e}')
    exit(1)
"

# Check frontend build
echo "=== Frontend Build ==="
if [ -d "/app/frontend/dist" ]; then
    echo "✓ Frontend build directory exists"
    ls -la /app/frontend/dist/ | head -5
else
    echo "✗ Frontend build directory missing"
fi

# Check if serve is available
if command -v serve &> /dev/null; then
    echo "✓ Serve is available for frontend"
else
    echo "✗ Serve not found - frontend serving may fail"
fi

# Test orchestrator startup (quick check)
echo "=== Testing Orchestrator Startup ==="
cd /app/orchestrator
timeout 10s python3 -c "
import sys
sys.path.insert(0, '/app/orchestrator')
try:
    from server import app
    print('✓ Orchestrator imports successfully')
except Exception as e:
    print(f'✗ Orchestrator import failed: {e}')
    exit(1)
" || echo "Orchestrator test completed (timeout expected)"

echo "=== Container Initialization Complete ==="
echo "Starting services with supervisor..."

# Execute the main command
exec "$@"