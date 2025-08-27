"""
Resource limit utilities for secure code execution.

This module provides utilities for enforcing CPU, memory, and other resource
limits during code compilation and execution to ensure system security and stability.
"""

import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import psutil


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
    
    def __post_init__(self):
        """Validate resource limits after initialization."""
        if self.time_ms <= 0:
            raise ValueError("time_ms must be positive")
        if self.cpu_time_ms <= 0:
            raise ValueError("cpu_time_ms must be positive")
        if self.memory_mb <= 0:
            raise ValueError("memory_mb must be positive")
        if self.stack_mb <= 0:
            raise ValueError("stack_mb must be positive")
        if self.file_size_mb <= 0:
            raise ValueError("file_size_mb must be positive")
        if self.open_files <= 0:
            raise ValueError("open_files must be positive")
        if self.processes <= 0:
            raise ValueError("processes must be positive")
    
    @classmethod
    def from_problem_config(cls, problem_data: Dict, overrides: Optional[Dict] = None) -> 'ResourceLimits':
        """
        Create ResourceLimits from problem configuration with optional overrides.
        
        Args:
            problem_data: Problem JSON data
            overrides: Optional limit overrides
            
        Returns:
            ResourceLimits instance
        """
        # Default limits
        limits = {
            "time_ms": 2000,
            "cpu_time_ms": 2000,
            "memory_mb": 256,
            "stack_mb": 64,
            "file_size_mb": 10,
            "open_files": 64,
            "processes": 1
        }
        
        # Apply problem-specific limits if present
        problem_limits = problem_data.get("limits", {})
        limits.update(problem_limits)
        
        # Apply user overrides
        if overrides:
            limits.update(overrides)
        
        return cls(**limits)
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary representation."""
        return {
            "time_ms": self.time_ms,
            "cpu_time_ms": self.cpu_time_ms,
            "memory_mb": self.memory_mb,
            "stack_mb": self.stack_mb,
            "file_size_mb": self.file_size_mb,
            "open_files": self.open_files,
            "processes": self.processes
        }


@dataclass
class ExecutionResult:
    """Result of a limited execution."""
    status: str  # "OK", "TIMEOUT", "MLE", "RE", "KILLED"
    exit_code: int = 0
    time_ms: Optional[int] = None
    memory_mb: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    signal: Optional[int] = None
    killed_by_limit: Optional[str] = None  # Which limit caused termination


class ResourceLimitEnforcer:
    """Enforces resource limits during process execution."""
    
    def __init__(self, limits: ResourceLimits):
        """
        Initialize the enforcer with resource limits.
        
        Args:
            limits: Resource limits to enforce
        """
        self.limits = limits
        self._process: Optional[subprocess.Popen] = None
        self._start_time: Optional[float] = None
        self._peak_memory: int = 0
    
    def run_with_limits(self, cmd: List[str], cwd: Optional[Path] = None, 
                       env: Optional[Dict[str, str]] = None,
                       stdin_data: Optional[str] = None) -> ExecutionResult:
        """
        Run a command with resource limits enforced.
        
        Args:
            cmd: Command and arguments to execute
            cwd: Working directory for execution
            env: Environment variables
            stdin_data: Data to send to stdin
            
        Returns:
            ExecutionResult with execution details
        """
        try:
            # Prepare environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            # Set up resource limits using preexec_fn
            def set_limits():
                self._set_process_limits()
            
            # Start process with limits
            self._start_time = time.time()
            self._process = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=exec_env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=set_limits,
                text=True
            )
            
            # Monitor execution
            return self._monitor_execution(stdin_data)
            
        except Exception as e:
            return ExecutionResult(
                status="RE",
                stderr=f"Failed to start process: {e}"
            )
    
    def _set_process_limits(self):
        """Set resource limits for the current process (called in child process)."""
        try:
            import resource
            
            # CPU time limit (seconds)
            cpu_time_sec = self.limits.cpu_time_ms / 1000.0
            resource.setrlimit(resource.RLIMIT_CPU, (int(cpu_time_sec), int(cpu_time_sec)))
            
            # Virtual memory limit (bytes)
            memory_bytes = self.limits.memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            
            # Stack size limit (bytes)
            stack_bytes = self.limits.stack_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_STACK, (stack_bytes, stack_bytes))
            
            # File size limit (bytes)
            file_size_bytes = self.limits.file_size_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_FSIZE, (file_size_bytes, file_size_bytes))
            
            # Open files limit
            resource.setrlimit(resource.RLIMIT_NOFILE, (self.limits.open_files, self.limits.open_files))
            
            # Process count limit
            resource.setrlimit(resource.RLIMIT_NPROC, (self.limits.processes, self.limits.processes))
            
        except ImportError:
            # resource module not available (Windows)
            pass
        except Exception:
            # Failed to set limits, continue anyway
            pass
    
    def _monitor_execution(self, stdin_data: Optional[str]) -> ExecutionResult:
        """
        Monitor process execution and enforce wall clock timeout.
        
        Args:
            stdin_data: Data to send to stdin
            
        Returns:
            ExecutionResult with execution details
        """
        if not self._process or not self._start_time:
            return ExecutionResult(status="RE", stderr="Process not started")
        
        try:
            # Communicate with timeout
            timeout_sec = self.limits.time_ms / 1000.0
            stdout, stderr = self._process.communicate(
                input=stdin_data,
                timeout=timeout_sec
            )
            
            # Calculate execution time
            execution_time = int((time.time() - self._start_time) * 1000)
            
            # Get memory usage
            memory_usage = self._get_peak_memory_usage()
            
            # Determine status
            status = self._determine_status(self._process.returncode, execution_time)
            
            return ExecutionResult(
                status=status,
                exit_code=self._process.returncode,
                time_ms=execution_time,
                memory_mb=memory_usage,
                stdout=stdout,
                stderr=stderr
            )
            
        except subprocess.TimeoutExpired:
            # Wall clock timeout exceeded
            self._kill_process()
            execution_time = int((time.time() - self._start_time) * 1000)
            
            return ExecutionResult(
                status="TIMEOUT",
                time_ms=execution_time,
                memory_mb=self._get_peak_memory_usage(),
                killed_by_limit="wall_clock_timeout",
                stderr="Process killed due to timeout"
            )
            
        except Exception as e:
            self._kill_process()
            return ExecutionResult(
                status="RE",
                stderr=f"Execution error: {e}"
            )
    
    def _kill_process(self):
        """Kill the running process and its children."""
        if not self._process:
            return
        
        try:
            # Kill process group to ensure all children are terminated
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
            else:
                self._process.kill()
            
            # Wait for process to terminate
            self._process.wait(timeout=1.0)
            
        except (ProcessLookupError, subprocess.TimeoutExpired, OSError):
            # Process already dead or couldn't be killed
            pass
    
    def _get_peak_memory_usage(self) -> int:
        """Get peak memory usage in MB."""
        if not self._process:
            return 0
        
        try:
            process = psutil.Process(self._process.pid)
            memory_info = process.memory_info()
            return int(memory_info.rss / (1024 * 1024))  # Convert to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0
    
    def _determine_status(self, exit_code: int, execution_time: int) -> str:
        """
        Determine execution status based on exit code and execution time.
        
        Args:
            exit_code: Process exit code
            execution_time: Execution time in milliseconds
            
        Returns:
            Status string
        """
        if exit_code == 0:
            return "OK"
        elif exit_code == -signal.SIGXCPU:
            return "TLE"  # CPU time limit exceeded
        elif exit_code == -signal.SIGKILL:
            return "MLE"  # Likely memory limit exceeded
        elif exit_code == -signal.SIGXFSZ:
            return "OLE"  # Output limit exceeded
        elif exit_code < 0:
            return "RE"   # Runtime error (signal)
        else:
            return "RE"   # Runtime error (non-zero exit)


def create_secure_temp_dir(base_dir: Optional[Path] = None) -> Path:
    """
    Create a secure temporary directory for code execution.
    
    Args:
        base_dir: Base directory for temp dir creation
        
    Returns:
        Path to created temporary directory
    """
    import tempfile
    
    if base_dir:
        temp_dir = tempfile.mkdtemp(dir=base_dir)
    else:
        temp_dir = tempfile.mkdtemp()
    
    temp_path = Path(temp_dir)
    
    # Set restrictive permissions (owner only)
    temp_path.chmod(0o700)
    
    return temp_path


def cleanup_temp_dir(temp_dir: Path):
    """
    Safely clean up a temporary directory.
    
    Args:
        temp_dir: Path to temporary directory to clean up
    """
    import shutil
    
    try:
        if temp_dir.exists() and temp_dir.is_dir():
            shutil.rmtree(temp_dir)
    except Exception:
        # Best effort cleanup, don't fail if we can't clean up
        pass