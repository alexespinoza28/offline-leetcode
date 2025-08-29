# Interview Coding Platform - Docker Setup

This directory contains Docker configuration and scripts for containerizing the Interview Coding Platform with all its dependencies and services.

## 🏗️ Architecture Overview

The Docker setup provides a complete containerized environment including:

- **Python Orchestrator**: Backend API with code execution capabilities
- **React Frontend**: Web interface for the coding platform
- **Multi-language Support**: Python, C++, C, Java, JavaScript runtimes
- **Database**: SQLite for progress tracking and metadata
- **Process Management**: Supervisor for managing multiple services

## 📁 Files Overview

```
docker/
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Service orchestration
├── supervisord.conf        # Process management configuration
├── entrypoint.sh           # Container initialization script
├── build.sh               # Build script
├── run.sh                 # Run script
├── dev-setup.sh           # Development environment setup
├── .dockerignore          # Docker ignore patterns
└── README.md              # This documentation
```

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
```

### Option 2: Using Build Scripts

```bash
# Build the image
./docker/build.sh

# Run the container
./docker/run.sh
```

### Option 3: Development Setup

```bash
# Set up development environment with hot reloading
./docker/dev-setup.sh

# Access development services
# Frontend: http://localhost:3001
# API: http://localhost:8001
```

## 🔧 Configuration

### Environment Variables

| Variable            | Default                           | Description               |
| ------------------- | --------------------------------- | ------------------------- |
| `NODE_ENV`          | `production`                      | Node.js environment       |
| `ORCHESTRATOR_HOST` | `0.0.0.0`                         | Orchestrator bind address |
| `ORCHESTRATOR_PORT` | `8000`                            | Orchestrator port         |
| `FRONTEND_PORT`     | `3000`                            | Frontend port             |
| `DATABASE_PATH`     | `/app/data/interview_platform.db` | SQLite database path      |
| `PROBLEMS_DIR`      | `/app/problems`                   | Problems directory        |
| `TEMPLATES_DIR`     | `/app/templates`                  | Templates directory       |
| `LOGS_DIR`          | `/app/logs`                       | Logs directory            |

### Volumes

- `interview_data`: Persistent database and user data
- `interview_logs`: Application logs
- Development volumes for hot reloading (dev profile only)

## 🏭 Production Deployment

### Using Docker Compose

```bash
# Production deployment
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker Directly

```bash
# Build production image
docker build -f docker/Dockerfile -t interview-platform:latest .

# Run with persistent volumes
docker run -d \
  --name interview-platform \
  -p 3000:3000 \
  -p 8000:8000 \
  -v interview_data:/app/data \
  -v interview_logs:/app/logs \
  --restart unless-stopped \
  interview-platform:latest
```

## 🛠️ Development

### Development Environment

The development setup provides:

- **Hot Reloading**: Source code changes reflected immediately
- **Volume Mounting**: Local code mounted into container
- **Separate Ports**: Avoid conflicts with production services
- **Debug Access**: Easy shell access for debugging

```bash
# Start development environment
./docker/dev-setup.sh

# Access development container
docker-compose exec interview-platform-dev bash

# View development logs
docker-compose --profile dev logs -f
```

### Debugging

```bash
# Shell access to running container
docker exec -it interview-coding-platform bash

# Check service status
docker exec -it interview-coding-platform supervisorctl status

# View specific service logs
docker exec -it interview-coding-platform tail -f /app/logs/orchestrator.log
docker exec -it interview-coding-platform tail -f /app/logs/frontend.log
```

## 🧪 Testing

### Automated Testing Script

Use the comprehensive test script to verify all functionality:

```bash
# Run the complete test suite
./docker/test-docker.sh
```

This script tests:

- API endpoints (health, problems, stats, analytics)
- Frontend accessibility on both ports
- Language runtimes (Python, Node.js, Java, C++)
- Database connectivity
- File permissions
- Container resource usage

### Manual Testing

#### Container Health Checks

```bash
# Check container health
docker ps --format "table {{.Names}}\\t{{.Status}}"

# Manual health check
curl http://localhost:8000/api/health
```

#### Service Testing

```bash
# Test orchestrator API
curl http://localhost:8000/api/health
curl http://localhost:8000/api/problems
curl http://localhost:8000/api/stats

# Test frontend
curl http://localhost:3000
curl http://localhost:8000  # Frontend also served here

# Test code execution (when problems are loaded)
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "two-sum",
    "language": "python",
    "code": "def solution(): return []"
  }'
```

#### Language Runtime Testing

```bash
# Test language runtimes inside container
docker exec interview-coding-platform python3 --version
docker exec interview-coding-platform node --version
docker exec interview-coding-platform java -version
docker exec interview-coding-platform g++ --version
```

## 📊 Monitoring

### Logs

```bash
# All logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f interview-platform

# Orchestrator logs only
docker exec -it interview-coding-platform tail -f /app/logs/orchestrator.log

# Frontend logs only
docker exec -it interview-coding-platform tail -f /app/logs/frontend.log
```

### Resource Usage

```bash
# Container resource usage
docker stats interview-coding-platform

# Disk usage
docker system df
docker images
docker volume ls
```

## 🔒 Security

### Container Security

- **Non-root User**: Application runs as `appuser`
- **Resource Limits**: CPU and memory limits configured
- **Network Isolation**: Services run in isolated network
- **Volume Permissions**: Proper file permissions set

### Code Execution Security

- **Sandboxed Execution**: Code runs in isolated environment
- **Resource Limits**: Time and memory limits enforced
- **Process Isolation**: Each execution in separate process
- **File System Restrictions**: Limited file system access

## 🚨 Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check container logs
docker logs interview-coding-platform

# Check system resources
docker system df
docker system prune  # Clean up if needed
```

#### Port Conflicts

```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000

# Use different ports
FRONTEND_PORT=3001 API_PORT=8001 docker-compose up
```

#### Database Issues

```bash
# Reset database
docker volume rm interview_data
docker-compose up --build

# Check database
docker exec -it interview-coding-platform sqlite3 /app/data/interview_platform.db ".tables"
```

#### Permission Issues

```bash
# Fix volume permissions
docker exec -it interview-coding-platform chown -R appuser:appuser /app/data /app/logs
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase container resources (if using Docker Desktop)
# Docker Desktop > Settings > Resources

# Clean up unused resources
docker system prune -a
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale with Docker Compose
docker-compose up --scale interview-platform=3

# Use load balancer (nginx, traefik, etc.)
# Configure load balancing across multiple containers
```

### Vertical Scaling

```bash
# Increase container resources
docker run --memory=2g --cpus=2 interview-platform:latest
```

## 🔄 Updates

### Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Or using scripts
./docker/build.sh
docker-compose restart
```

### Database Migrations

```bash
# Backup database
docker exec interview-coding-platform cp /app/data/interview_platform.db /app/data/backup.db

# Run migrations (if needed)
docker exec interview-coding-platform python3 /app/orchestrator/migrate.py
```

## 📋 Maintenance

### Regular Maintenance

```bash
# Clean up unused Docker resources
docker system prune -a

# Update base images
docker pull ubuntu:22.04
docker-compose build --no-cache

# Backup data
docker run --rm -v interview_data:/data -v $(pwd):/backup ubuntu tar czf /backup/data-backup.tar.gz -C /data .
```

### Log Rotation

Logs are automatically rotated by supervisor configuration:

- Maximum size: 10MB per log file
- Keep 3 backup files
- Automatic rotation when size limit reached

## 🆘 Support

For issues and questions:

1. Check the logs: `docker-compose logs -f`
2. Verify health checks: `curl http://localhost:8000/health`
3. Check resource usage: `docker stats`
4. Review this documentation
5. Check the main project README.md

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Supervisor Documentation](http://supervisord.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
