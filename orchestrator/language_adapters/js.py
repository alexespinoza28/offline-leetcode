"""
Node.js language adapter.

This module implements the Node.js language adapter for executing JavaScript code
with proper resource limits.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

from .base import LanguageAdapter, CompileResult, RunResult, ResourceLimits


class NodeAdapter(LanguageAdapter):
    """Language adapter for Node.js."""

    def __init__(self):
        super().__init__()
        self.name = "js"
        self.entry_file = "main.js"
        self.runtime_cmd = ["node", "main.js"]

    def compile(self, workdir: Path) -> CompileResult:
        """
        Compile JavaScript code (syntax check).

        For Node.js, compilation is essentially a syntax check using `node -c`.

        Args:
            workdir: Path to directory containing JavaScript source code

        Returns:
            CompileResult with syntax check status and any error messages
        """
        start_time = time.time()
        entry_path = workdir / self.entry_file

        if not entry_path.exists():
            return CompileResult(
                success=False,
                stderr=f"Entry file {self.entry_file} not found",
                exit_code=1,
                compile_time_ms=0
            )

        # Prepare compilation command
        cmd = ["node", "-c", str(entry_path)]

        try:
            # Run compilation (syntax check)
            result = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=30  # 30 second compilation timeout
            )

            compile_time_ms = int((time.time() - start_time) * 1000)

            if result.returncode == 0:
                return CompileResult(
                    success=True,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=0,
                    compile_time_ms=compile_time_ms
                )
            else:
                return CompileResult(
                    success=False,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    compile_time_ms=compile_time_ms
                )

        except subprocess.TimeoutExpired:
            compile_time_ms = int((time.time() - start_time) * 1000)

            return CompileResult(
                success=False,
                stderr="Syntax check timed out after 30 seconds",
                exit_code=124,
                compile_time_ms=compile_time_ms
            )
        except FileNotFoundError:
            return CompileResult(
                success=False,
                stderr="node command not found",
                exit_code=127,
                compile_time_ms=0
            )
        except Exception as e:
            compile_time_ms = int((time.time() - start_time) * 1000)

            return CompileResult(
                success=False,
                stderr=f"Unexpected error during syntax check: {str(e)}",
                exit_code=1,
                compile_time_ms=compile_time_ms
            )

    def run(self, workdir: Path, stdin_path: Path, stdout_path: Path,
            limits: ResourceLimits) -> RunResult:
        """
        Execute Node.js code with resource limits.

        Args:
            workdir: Path to directory containing Node.js code
            stdin_path: Path to input file
            stdout_path: Path to output file
            limits: Resource limits to enforce

        Returns:
            RunResult with execution status and metrics
        """
        start_time = time.time()

        # Prepare command
        cmd = ["node", f"--max-old-space-size={limits.memory_mb}", self.entry_file]

        try:
            # Open input and output files
            with open(stdin_path, 'r') as stdin_file, \
                 open(stdout_path, 'w') as stdout_file:

                # Execute with timeout and resource limits
                process = subprocess.Popen(
                    cmd,
                    cwd=workdir,
                    stdin=stdin_file,
                    stdout=stdout_file,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=self._set_resource_limits(limits) if hasattr(os, 'setrlimit') else None
                )

                try:
                    # Wait for process with timeout
                    stderr_output, _ = process.communicate(timeout=limits.time_ms / 1000.0)
                    exit_code = process.returncode

                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                    execution_time_ms = int((time.time() - start_time) * 1000)

                    return RunResult(
                        status="TIMEOUT",
                        exit_code=124,
                        time_ms=execution_time_ms,
                        stderr="Process timed out",
                        signal=9
                    )

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Read stdout content
            stdout_content = ""
            if stdout_path.exists():
                with open(stdout_path, 'r') as f:
                    stdout_content = f.read()

            # Determine status based on exit code
            if exit_code == 0:
                status = "OK"
            elif exit_code == 137:  # SIGKILL (memory limit)
                status = "MLE"
            elif exit_code == 139:  # SIGSEGV
                status = "RE"
            else:
                status = "RE"

            return RunResult(
                status=status,
                exit_code=exit_code,
                time_ms=execution_time_ms,
                stdout=stdout_content,
                stderr=stderr_output or "",
                signal=None if exit_code >= 0 else abs(exit_code)
            )

        except FileNotFoundError:
            return RunResult(
                status="RE",
                exit_code=127,
                stderr="node command not found",
                time_ms=0
            )
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)

            return RunResult(
                status="RE",
                exit_code=1,
                time_ms=execution_time_ms,
                stderr=f"Execution error: {str(e)}"
            )

    def _set_resource_limits(self, limits: ResourceLimits):
        """
        Create a preexec_fn to set resource limits for the subprocess.

        Args:
            limits: Resource limits to apply

        Returns:
            Function to be used as preexec_fn in subprocess.Popen
        """
        def set_limits():
            import resource

            # Set memory limit (virtual memory)
            if limits.memory_mb > 0:
                memory_bytes = limits.memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

            # Set stack size limit
            if limits.stack_mb > 0:
                stack_bytes = limits.stack_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_STACK, (stack_bytes, stack_bytes))

            # Set file size limit
            if limits.file_size_mb > 0:
                file_bytes = limits.file_size_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))

            # Set open files limit
            if limits.open_files > 0:
                resource.setrlimit(resource.RLIMIT_NOFILE, (limits.open_files, limits.open_files))

            # Set process limit
            if limits.processes > 0:
                resource.setrlimit(resource.RLIMIT_NPROC, (limits.processes, limits.processes))

        return set_limits

    def get_template_content(self) -> str:
        """
        Get Node.js template content.

        Returns:
            Node.js template source code
        """
        return '''const fs = require('fs');

function solve(input) {
    // Your solution here
    return "";
}

const input = fs.readFileSync(0, 'utf8');
const output = solve(input);
process.stdout.write(output);
'''

    def validate_solution(self, workdir: Path) -> bool:
        """
        Validate that Node.js solution file exists and has basic structure.

        Args:
            workdir: Path to directory to validate

        Returns:
            True if solution file is present and appears valid
        """
        entry_path = workdir / self.entry_file

        if not entry_path.exists() or not entry_path.is_file():
            return False

        try:
            # Basic validation: check if file can be read and has some content
            with open(entry_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # File should not be empty
            if not content:
                return False

            return True

        except Exception:
            return False
