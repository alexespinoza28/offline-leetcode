#!/bin/bash
set -e

# Run script for Interview Coding Platform Docker container

echo "=== Running Interview Coding Platform ==="

# Configuration
IMAGE_NAME="interview-coding-platform:latest"
CONTAINER_NAME="interview-coding-platform"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
API_PORT="${API_PORT:-8000}"

# Check if container is already running
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "Container $CONTAINER_NAME is already running"
    echo "Stopping existing container..."
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
fi

# Create volumes if they don't exist
docker volume create interview_data 2>/dev/null || true
docker volume create interview_logs 2>/dev/null || true

echo "Starting container: $CONTAINER_NAME"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "API: http://localhost:$API_PORT"

# Run the container
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$FRONTEND_PORT:3000" \
    -p "$API_PORT:8000" \
    -v interview_data:/app/data \
    -v interview_logs:/app/logs \
    --restart unless-stopped \
    "$IMAGE_NAME"

echo "=== Container Started ==="
echo "Container ID: $(docker ps -q -f name="$CONTAINER_NAME")"

# Show logs for a few seconds
echo "=== Initial Logs ==="
sleep 3
docker logs --tail 20 "$CONTAINER_NAME"

echo ""
echo "=== Container Status ==="
docker ps -f name="$CONTAINER_NAME"

echo ""
echo "=== Access Information ==="
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "API: http://localhost:$API_PORT"
echo "Health Check: http://localhost:$API_PORT/health"

echo ""
echo "=== Useful Commands ==="
echo "View logs: docker logs -f $CONTAINER_NAME"
echo "Stop container: docker stop $CONTAINER_NAME"
echo "Remove container: docker rm $CONTAINER_NAME"
echo "Shell access: docker exec -it $CONTAINER_NAME bash"