#!/usr/bin/env python3
"""
Startup script for the orchestrator server.
This script handles the module import issues when running in Docker.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

# Now import and run the server
if __name__ == "__main__":
    from orchestrator.server import app
    import uvicorn
    
    # Get configuration from environment
    host = os.environ.get("ORCHESTRATOR_HOST", "0.0.0.0")
    port = int(os.environ.get("ORCHESTRATOR_PORT", "8000"))
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )