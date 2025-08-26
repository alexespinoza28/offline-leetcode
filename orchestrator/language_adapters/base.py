"""
Base interface for language adapters.

This module defines the abstract base class that all language adapters must implement
to provide consistent compilation and execution capabilities across different programming languages.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ResourceLimits:
    """Resource limits for code execution."""
    time_ms: int = 2000          # Wall clock timeout
    cpu_time_ms: int = 2000      # CPU time limit
    memory_mb: int = 256         # Virtual memory limit
    stack_mb: int = 64           # Stack size limit
    file_size_mb: int = 10       # Output file size limit
    open_files: int = 64         # File descriptor limit
    processes: int = 1           # Process count limit


@dataclass
class CompileResult:
    """Result of compilation process."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    compile_time_ms: Optional[int] = None


@dataclass
class RunResult:
    """Result of code execution."""
    status: str  # OK, TIMEOUT, MLE, RE, etc.
    exit_code: int = 0
    time_ms: Optional[int] = None
    memory_mb: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    signal: Optional[int] = None


class LanguageAdapter(ABC):
    """Abstract base class for language adapters."""
    
    def __init__(self):
        self.name: str = ""
        self.entry_file: str = ""
        self.runtime_cmd: List[str] = []
    
    @abstractmethod
    def compile(self, workdir: Path) -> CompileResult:
        """
        Compile source code in the given working directory.
        
        Args:
            workdir: Path to directory containing source code
            
        Returns:
            CompileResult with compilation status and logs
        """
        pass
    
    @abstractmethod
    def run(self, workdir: Path, stdin_path: Path, stdout_path: Path, 
            limits: ResourceLimits) -> RunResult:
        """
        Execute compiled code with resource limits.
        
        Args:
            workdir: Path to directory containing compiled code
            stdin_path: Path to input file
            stdout_path: Path to output file
            limits: Resource limits to enforce
            
        Returns:
            RunResult with execution status and metrics
        """
        pass
    
    def get_template_content(self) -> str:
        """
        Get template content for this language.
        
        Returns:
            Template source code as string
        """
        return ""
    
    def validate_solution(self, workdir: Path) -> bool:
        """
        Validate that required solution files exist.
        
        Args:
            workdir: Path to directory to validate
            
        Returns:
            True if solution files are present and valid
        """
        entry_path = workdir / self.entry_file
        return entry_path.exists() and entry_path.is_file()