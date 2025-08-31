#!/bin/bash

# Start the backend server in the background
python3 orchestrator/start_server.py &

# Get the PID of the last background command
SERVER_PID=$!

echo "Backend server started with PID: $SERVER_PID"
echo "Access it at http://0.0.0.0:8000"
echo "To stop the server, run: kill $SERVER_PID"
