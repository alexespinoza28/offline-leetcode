# Multi-stage build for interview coding platform
# This Dockerfile creates a comprehensive environment with all dependencies
# for the interview coding platform including multiple language support

# =============================================================================
# Stage 1: Base system with all language runtimes
# =============================================================================
FROM ubuntu:22.04 AS base

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies and language runtimes
RUN apt-get update && apt-get install -y \
    # Basic system tools
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    # Build tools
    build-essential \
    make \
    cmake \
    # C/C++ development
    gcc \
    g++ \
    gdb \
    valgrind \
    # Python development
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # Java development
    openjdk-17-jdk \
    openjdk-17-jre \
    # Database
    sqlite3 \
    # Process management
    supervisor \
    # Security and limits
    cgroup-tools \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install latest Node.js LTS (remove conflicting packages first)
RUN apt-get update && apt-get remove -y nodejs npm libnode-dev || true \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g serve \
    && rm -rf /var/lib/apt/lists/*

# Verify installations
RUN python3 --version && \
    node --version && \
    npm --version && \
    java -version && \
    gcc --version && \
    g++ --version

# =============================================================================
# Stage 2: Frontend build
# =============================================================================
FROM base AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./

# Clear npm cache and install dependencies
RUN npm cache clean --force \
    && rm -rf node_modules package-lock.json \
    && npm install

# Copy frontend source
COPY frontend/ ./

# Build frontend with explicit platform
RUN npm run build

# =============================================================================
# Stage 3: Python dependencies
# =============================================================================
FROM base AS python-builder

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY orchestrator/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# =============================================================================
# Stage 4: Final production image
# =============================================================================
FROM base AS production

# Create application user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /bin/bash -c "Application User" appuser

# Create necessary directories
RUN mkdir -p /app/orchestrator \
             /app/frontend \
             /app/problems \
             /app/templates \
             /app/data \
             /app/logs \
             /var/log/supervisor \
    && chown -R appuser:appuser /app

# Copy Python virtual environment
COPY --from=python-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy built frontend (Vite builds to dist/)
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
COPY --from=frontend-builder /app/frontend/package*.json /app/frontend/

# Copy orchestrator source
COPY orchestrator/ /app/orchestrator/

# Copy configuration files
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/entrypoint.sh /app/entrypoint.sh

# Set up permissions
RUN chown -R appuser:appuser /app && \
    chmod +x /app/entrypoint.sh

# Create problems directory structure
RUN mkdir -p /app/problems/examples \
             /app/problems/templates \
    && chown -R appuser:appuser /app/problems

# Set up SQLite database directory
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app/data

# Configure environment variables
ENV PYTHONPATH="/app/orchestrator:$PYTHONPATH"
ENV NODE_ENV=production
ENV ORCHESTRATOR_HOST=0.0.0.0
ENV ORCHESTRATOR_PORT=8000
ENV FRONTEND_PORT=3000
ENV DATABASE_PATH=/app/data/interview_platform.db
ENV PROBLEMS_DIR=/app/problems
ENV TEMPLATES_DIR=/app/templates
ENV LOGS_DIR=/app/logs

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Set working directory
WORKDIR /app

# Create database initialization script
RUN echo '#!/usr/bin/env python3' > /app/init_db.py && \
    echo 'import sqlite3' >> /app/init_db.py && \
    echo 'import os' >> /app/init_db.py && \
    echo 'from pathlib import Path' >> /app/init_db.py && \
    echo '' >> /app/init_db.py && \
    echo 'db_path = os.environ.get("DATABASE_PATH", "/app/data/interview_platform.db")' >> /app/init_db.py && \
    echo 'Path(db_path).parent.mkdir(parents=True, exist_ok=True)' >> /app/init_db.py && \
    echo '' >> /app/init_db.py && \
    echo 'conn = sqlite3.connect(db_path)' >> /app/init_db.py && \
    echo 'cursor = conn.cursor()' >> /app/init_db.py && \
    echo '' >> /app/init_db.py && \
    echo 'try:' >> /app/init_db.py && \
    echo '    with open("/app/orchestrator/db/schema.sql", "r") as f:' >> /app/init_db.py && \
    echo '        schema = f.read()' >> /app/init_db.py && \
    echo '    cursor.executescript(schema)' >> /app/init_db.py && \
    echo '    conn.commit()' >> /app/init_db.py && \
    echo '    print("Database initialized successfully")' >> /app/init_db.py && \
    echo 'except Exception as e:' >> /app/init_db.py && \
    echo '    print(f"Database initialization error: {e}")' >> /app/init_db.py && \
    echo 'finally:' >> /app/init_db.py && \
    echo '    conn.close()' >> /app/init_db.py && \
    chmod +x /app/init_db.py

# Entry point
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]