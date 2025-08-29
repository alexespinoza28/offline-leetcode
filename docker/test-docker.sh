#!/bin/bash
set -e

echo "=== Docker Container Testing Script ==="
echo "Testing Interview Coding Platform Docker setup"
echo ""

# Configuration
FRONTEND_PORT=3000
API_PORT=8000
CONTAINER_NAME="interview-coding-platform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Test function
test_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    print_info "Testing: $description"
    
    if response=$(curl -s -w "%{http_code}" "$url" 2>/dev/null); then
        status_code="${response: -3}"
        body="${response%???}"
        
        if [ "$status_code" -eq "$expected_status" ]; then
            print_success "$description - Status: $status_code"
            if [ ${#body} -gt 100 ]; then
                echo "  Response: ${body:0:100}..."
            else
                echo "  Response: $body"
            fi
        else
            print_error "$description - Expected: $expected_status, Got: $status_code"
            return 1
        fi
    else
        print_error "$description - Connection failed"
        return 1
    fi
    echo ""
}

# Check if container is running
print_info "Checking if container is running..."
if docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    print_success "Container $CONTAINER_NAME is running"
else
    print_error "Container $CONTAINER_NAME is not running"
    echo "Please start the container first:"
    echo "  docker-compose up -d"
    echo "  or"
    echo "  docker run -d --name $CONTAINER_NAME -p $FRONTEND_PORT:3000 -p $API_PORT:8000 interview-coding-platform:latest"
    exit 1
fi

echo ""
print_info "Waiting for services to be ready..."
sleep 5

echo ""
echo "=== Testing API Endpoints ==="

# Test health endpoint
test_endpoint "http://localhost:$API_PORT/api/health" 200 "Health check"

# Test problems endpoint
test_endpoint "http://localhost:$API_PORT/api/problems" 200 "Problems list"

# Test stats endpoint
test_endpoint "http://localhost:$API_PORT/api/stats" 200 "Execution stats"

# Test analytics overview
test_endpoint "http://localhost:$API_PORT/api/analytics/overview" 200 "Analytics overview"

echo ""
echo "=== Testing Frontend ==="

# Test frontend on both ports
test_endpoint "http://localhost:$FRONTEND_PORT/" 200 "Frontend (dedicated port)"
test_endpoint "http://localhost:$API_PORT/" 200 "Frontend (API port)"

echo ""
echo "=== Testing Container Health ==="

# Check container logs for errors
print_info "Checking container logs for errors..."
if docker logs "$CONTAINER_NAME" 2>&1 | grep -i "error\|failed\|exception" | grep -v "404" | head -5; then
    print_error "Found errors in container logs (shown above)"
else
    print_success "No critical errors found in container logs"
fi

# Check service status via supervisor
print_info "Checking service status..."
if docker exec "$CONTAINER_NAME" supervisorctl status 2>/dev/null; then
    print_success "Supervisor services status retrieved"
else
    print_error "Could not get supervisor status"
fi

echo ""
echo "=== Testing Language Runtimes ==="

# Test language runtimes inside container
print_info "Testing Python runtime..."
if docker exec "$CONTAINER_NAME" python3 --version >/dev/null 2>&1; then
    version=$(docker exec "$CONTAINER_NAME" python3 --version)
    print_success "Python runtime: $version"
else
    print_error "Python runtime not available"
fi

print_info "Testing Node.js runtime..."
if docker exec "$CONTAINER_NAME" node --version >/dev/null 2>&1; then
    version=$(docker exec "$CONTAINER_NAME" node --version)
    print_success "Node.js runtime: $version"
else
    print_error "Node.js runtime not available"
fi

print_info "Testing Java runtime..."
if docker exec "$CONTAINER_NAME" java -version >/dev/null 2>&1; then
    version=$(docker exec "$CONTAINER_NAME" java -version 2>&1 | head -1)
    print_success "Java runtime: $version"
else
    print_error "Java runtime not available"
fi

print_info "Testing C++ compiler..."
if docker exec "$CONTAINER_NAME" g++ --version >/dev/null 2>&1; then
    version=$(docker exec "$CONTAINER_NAME" g++ --version | head -1)
    print_success "C++ compiler: $version"
else
    print_error "C++ compiler not available"
fi

echo ""
echo "=== Testing Database ==="

print_info "Checking database..."
if docker exec "$CONTAINER_NAME" test -f /app/data/interview_platform.db; then
    print_success "Database file exists"
    
    # Test database connection
    if docker exec "$CONTAINER_NAME" sqlite3 /app/data/interview_platform.db ".tables" >/dev/null 2>&1; then
        tables=$(docker exec "$CONTAINER_NAME" sqlite3 /app/data/interview_platform.db ".tables")
        print_success "Database connection successful"
        echo "  Tables: $tables"
    else
        print_error "Database connection failed"
    fi
else
    print_info "Database file not found (will be created on first use)"
fi

echo ""
echo "=== Testing File Permissions ==="

print_info "Checking file permissions..."
if docker exec "$CONTAINER_NAME" test -w /app/data; then
    print_success "Data directory is writable"
else
    print_error "Data directory is not writable"
fi

if docker exec "$CONTAINER_NAME" test -w /app/logs; then
    print_success "Logs directory is writable"
else
    print_error "Logs directory is not writable"
fi

echo ""
echo "=== Resource Usage ==="

print_info "Container resource usage:"
docker stats "$CONTAINER_NAME" --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo "=== Test Summary ==="

# Count successful tests (this is a simple approach)
if curl -s http://localhost:$API_PORT/api/health >/dev/null 2>&1 && \
   curl -s http://localhost:$FRONTEND_PORT/ >/dev/null 2>&1; then
    print_success "Core functionality is working"
    echo ""
    echo "🎉 Docker container is ready for use!"
    echo ""
    echo "Access the application:"
    echo "  Frontend: http://localhost:$FRONTEND_PORT"
    echo "  API: http://localhost:$API_PORT"
    echo "  Health Check: http://localhost:$API_PORT/api/health"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker logs $CONTAINER_NAME"
    echo "  Shell access: docker exec -it $CONTAINER_NAME bash"
    echo "  Stop container: docker-compose down"
    echo "  Restart services: docker exec $CONTAINER_NAME supervisorctl restart all"
else
    print_error "Core functionality is not working properly"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check container logs: docker logs $CONTAINER_NAME"
    echo "  2. Check service status: docker exec $CONTAINER_NAME supervisorctl status"
    echo "  3. Restart container: docker-compose restart"
    exit 1
fi