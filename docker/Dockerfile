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

# Install code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh

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

# Expose code-server port
EXPOSE 8080

# Start code-server
CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "none", "/workspace"]