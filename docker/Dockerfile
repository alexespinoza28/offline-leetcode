# Multi-stage build for interview coding platform
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    gcc \
    g++ \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    openjdk-17-jdk \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install code-server (optional for development)
# RUN curl -fsSL https://code-server.dev/install.sh | sh

# Create non-root user for security
RUN useradd -m -s /bin/bash coder && \
    echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up workspace
WORKDIR /workspace
COPY . /workspace/
RUN chown -R coder:coder /workspace

# Switch to non-root user
USER coder

# Install Python dependencies
RUN python3 -m pip install --user --upgrade pip

# Install Node.js dependencies for frontend
WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm install

# Build frontend
COPY frontend/ ./
RUN npm run build

# Switch back to workspace root
WORKDIR /workspace

# Install Python orchestrator dependencies
COPY orchestrator/requirements.txt ./orchestrator/
RUN python3 -m pip install --user -r orchestrator/requirements.txt

# Expose ports: 3000 for frontend, 8000 for API
EXPOSE 3000 8000

# Start both frontend and orchestrator
CMD ["sh", "-c", "cd /workspace/orchestrator && python3 server.py & cd /workspace/frontend && npm run preview -- --port 3000 --host 0.0.0.0"]