#!/bin/bash
set -e

# Development setup script for Interview Coding Platform

echo "=== Interview Coding Platform - Development Setup ==="

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Change to project root
cd "$(dirname "$0")/.."

# Create necessary directories
echo "Creating development directories..."
mkdir -p problems/examples
mkdir -p templates/explanations
mkdir -p data
mkdir -p logs

# Create sample problem for testing
if [ ! -f "problems/examples/two-sum/problem.json" ]; then
    echo "Creating sample problem..."
    mkdir -p problems/examples/two-sum
    
    cat > problems/examples/two-sum/problem.json << 'EOF'
{
  "slug": "two-sum",
  "title": "Two Sum",
  "difficulty": "Easy",
  "tags": ["Array", "Hash Table"],
  "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
  "examples": [
    {
      "input": "nums = [2,7,11,15], target = 9",
      "output": "[0,1]",
      "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
    }
  ],
  "constraints": [
    "2 <= nums.length <= 10^4",
    "-10^9 <= nums[i] <= 10^9",
    "-10^9 <= target <= 10^9",
    "Only one valid answer exists."
  ]
}
EOF

    # Create sample solution
    cat > problems/examples/two-sum/solution.py << 'EOF'
def two_sum(nums, target):
    """
    Find two numbers in the array that add up to target.
    """
    num_dict = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[num] = i
    return []

if __name__ == "__main__":
    # Test the solution
    nums = [2, 7, 11, 15]
    target = 9
    result = two_sum(nums, target)
    print(f"Input: nums = {nums}, target = {target}")
    print(f"Output: {result}")
EOF

    echo "✅ Sample problem created"
fi

# Build the Docker image
echo "Building Docker image..."
./docker/build.sh

# Create development environment file
cat > .env.development << 'EOF'
# Development environment variables
NODE_ENV=development
ORCHESTRATOR_HOST=0.0.0.0
ORCHESTRATOR_PORT=8000
FRONTEND_PORT=3000
DATABASE_PATH=/app/data/interview_platform.db
PROBLEMS_DIR=/app/problems
TEMPLATES_DIR=/app/templates
LOGS_DIR=/app/logs
EOF

echo "✅ Development environment file created"

# Start development services
echo "Starting development services..."
docker-compose --profile dev up -d

echo "=== Development Setup Complete ==="
echo ""
echo "🚀 Services are starting up..."
echo "   Frontend: http://localhost:3001"
echo "   API: http://localhost:8001"
echo "   Health Check: http://localhost:8001/health"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Shell access: docker-compose exec interview-platform-dev bash"
echo ""
echo "🔧 Development features:"
echo "   - Hot reloading enabled"
echo "   - Source code mounted as volumes"
echo "   - Separate ports to avoid conflicts"
echo ""
echo "⏳ Please wait 30-60 seconds for services to fully start up..."