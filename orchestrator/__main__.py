#!/usr/bin/env python3
"""
Entry point for running the orchestrator as a module.

Usage:
    python -m orchestrator run --problem two-sum --lang python --code "..."
    python -m orchestrator explain --problem two-sum --lang python
    python -m orchestrator gen-tests --problem two-sum --count 10
"""

from .cli import main

if __name__ == "__main__":
    exit(main())