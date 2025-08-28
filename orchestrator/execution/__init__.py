"""
Code execution engine for the interview coding platform.

This module provides secure, sandboxed code execution with resource limits
and comprehensive test case management.
"""

from .executor import (
    CodeExecutor,
    ExecutionStatus,
    ExecutionResult,
    TestCase,
    TestCaseResult
)

from .service import ExecutionService, execution_service

__all__ = [
    "CodeExecutor",
    "ExecutionStatus", 
    "ExecutionResult",
    "TestCase",
    "TestCaseResult",
    "ExecutionService",
    "execution_service"
]