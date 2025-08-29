#!/bin/bash
set -e

# Build script for Interview Coding Platform Docker image

echo "=== Building Interview Coding Platform Docker Image ==="

# Configuration
IMAGE_NAME="interview-coding-platform"
IMAGE_TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# Build arguments
BUILD_ARGS=""
if [ -n "$BUILD_DATE" ]; then
    BUILD_ARGS="$BUILD_ARGS --build-arg BUILD_DATE=$BUILD_DATE"
fi

if [ -n "$VCS_REF" ]; then
    BUILD_ARGS="$BUILD_ARGS --build-arg VCS_REF=$VCS_REF"
fi

# Change to project root
cd "$(dirname "$0")/.."

echo "Building image: $FULL_IMAGE_NAME"
echo "Build context: $(pwd)"

# Build the image
docker build \
    -f docker/Dockerfile \
    -t "$FULL_IMAGE_NAME" \
    $BUILD_ARGS \
    .

echo "=== Build Complete ==="
echo "Image: $FULL_IMAGE_NAME"
echo "Size: $(docker images --format "table {{.Size}}" "$FULL_IMAGE_NAME" | tail -n 1)"

# Test the image
echo "=== Testing Image ==="
docker run --rm "$FULL_IMAGE_NAME" python3 --version
docker run --rm "$FULL_IMAGE_NAME" node --version
docker run --rm "$FULL_IMAGE_NAME" java -version

echo "=== Image Ready ==="
echo "To run the container:"
echo "  docker run -p 3000:3000 -p 8000:8000 $FULL_IMAGE_NAME"
echo ""
echo "To run with docker-compose:"
echo "  docker-compose up"