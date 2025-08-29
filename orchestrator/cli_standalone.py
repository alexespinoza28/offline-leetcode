#!/usr/bin/env python3
"""
Standalone CLI script for testing the orchestrator CLI functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock the relative imports
import utils.schema
from cli import OrchestatorCLI

if __name__ == "__main__":
    cli = OrchestatorCLI()
    sys.exit(cli.run())