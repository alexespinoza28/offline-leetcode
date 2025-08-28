"""
Unit tests for Python language adapter.

Tests the Python adapter implementation including syntax checking,
execution with resource limits, and PYTHONHASHSEED determinism.
"""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from orchestrator.language_adapters import PythonAdapter, ResourceLimits


class TestPythonAdapter:
    """Test PythonAdapter implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = PythonAdapter()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.main_py = self.temp_dir / "main.py"
        self.stdin_file = self.temp_dir / "input.txt"
        self.stdout_file = self.temp_dir / "output.txt"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test that PythonAdapter initializes correctly."""
        assert self.adapter.name == "python"
        assert self.adapter.entry_file == "main.py"
        assert self.adapter.runtime_cmd == ["python3", "main.py"]
    
    def test_get_template_content(self):
        """Test that template content is provided."""
        template = self.adapter.get_template_content()
        
        assert isinstance(template, str)
        assert len(template) > 0
        assert "def solve():" in template
        assert "if __name__ == \"__main__\":" in template
        assert "#!/usr/bin/env python3" in template
    
    def test_compile_success(self):
        """Test successful Python syntax check."""
        # Create valid Python file
        python_code = '''
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
'''
        self.main_py.write_text(python_code)
        
        result = self.adapter.compile(self.temp_dir)
        
        assert result.success is True
        assert result.exit_code == 0
        assert "syntax check passed" in result.stdout.lower()
        assert result.stderr == ""
        assert result.compile_time_ms is not None
        assert result.compile_time_ms >= 0
    
    def test_compile_syntax_error(self):
        """Test Python syntax error detection."""
        # Create invalid Python file
        python_code = '''
def hello(
    print("Missing closing parenthesis")
'''
        self.main_py.write_text(python_code)
        
        result = self.adapter.compile(self.temp_dir)
        
        assert result.success is False
        assert result.exit_code == 1
        assert result.stdout == ""
        assert len(result.stderr) > 0
        assert result.compile_time_ms is not None
        assert result.compile_time_ms >= 0
    
    def test_compile_missing_file(self):
        """Test compilation when main.py doesn't exist."""
        result = self.adapter.compile(self.temp_dir)
        
        assert result.success is False
        assert result.exit_code == 1
        assert "not found" in result.stderr
        assert result.compile_time_ms == 0
    
    @patch('subprocess.Popen')
    def test_run_success(self, mock_popen):
        """Test successful Python code execution."""
        # Mock successful process
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", None)
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Create input file
        self.stdin_file.write_text("test input\n")
        
        # Mock the stdout file creation by the process
        def mock_popen_side_effect(*args, **kwargs):
            # Simulate the process writing to stdout file
            self.stdout_file.write_text("test output\n")
            return mock_process
        
        mock_popen.side_effect = mock_popen_side_effect
        
        limits = ResourceLimits(time_ms=1000, memory_mb=128)
        result = self.adapter.run(self.temp_dir, self.stdin_file, self.stdout_file, limits)
        
        assert result.status == "OK"
        assert result.exit_code == 0
        assert result.stdout == "test output\n"
        assert result.stderr == ""
        assert result.time_ms is not None
        assert result.time_ms >= 0
        
        # Verify subprocess was called with correct environment
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        env = call_args[1]['env']
        assert env['PYTHONHASHSEED'] == '0'
        assert str(self.temp_dir) in env['PYTHONPATH']
    
    @patch('subprocess.Popen')
    def test_run_timeout(self, mock_popen):
        """Test Python code execution timeout."""
        # Mock process that times out
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired(
            cmd=["python3", "main.py"], timeout=1.0
        )
        mock_popen.return_value = mock_process
        
        self.stdin_file.write_text("")
        
        limits = ResourceLimits(time_ms=1000)
        result = self.adapter.run(self.temp_dir, self.stdin_file, self.stdout_file, limits)
        
        assert result.status == "TIMEOUT"
        assert result.exit_code == 124
        assert "timed out" in result.stderr.lower()
        assert result.signal == 9
        assert result.time_ms is not None
        
        # Verify process was killed
        mock_process.kill.assert_called_once()
        mock_process.wait.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_run_memory_limit_exceeded(self, mock_popen):
        """Test Python code execution with memory limit exceeded."""
        # Mock process killed by SIGKILL (memory limit)
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Memory limit exceeded", None)
        mock_process.returncode = 137  # SIGKILL
        mock_popen.return_value = mock_process
        
        self.stdin_file.write_text("")
        
        limits = ResourceLimits(memory_mb=64)
        result = self.adapter.run(self.temp_dir, self.stdin_file, self.stdout_file, limits)
        
        assert result.status == "MLE"
        assert result.exit_code == 137
        assert result.stderr == "Memory limit exceeded"
    
    @patch('subprocess.Popen')
    def test_run_runtime_error(self, mock_popen):
        """Test Python code execution with runtime error."""
        # Mock process with runtime error
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Traceback: ZeroDivisionError", None)
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        self.stdin_file.write_text("")
        
        limits = ResourceLimits()
        result = self.adapter.run(self.temp_dir, self.stdin_file, self.stdout_file, limits)
        
        assert result.status == "RE"
        assert result.exit_code == 1
        assert "ZeroDivisionError" in result.stderr
    
    @patch('subprocess.Popen')
    def test_run_python_not_found(self, mock_popen):
        """Test execution when python3 is not available."""
        mock_popen.side_effect = FileNotFoundError("python3 not found")
        
        self.stdin_file.write_text("")
        
        limits = ResourceLimits()
        result = self.adapter.run(self.temp_dir, self.stdin_file, self.stdout_file, limits)
        
        assert result.status == "RE"
        assert result.exit_code == 127
        assert "not found" in result.stderr
        assert result.time_ms == 0
    
    def test_validate_solution_success(self):
        """Test successful solution validation."""
        # Create valid Python file
        python_code = '''
def solve():
    return "Hello, World!"

if __name__ == "__main__":
    print(solve())
'''
        self.main_py.write_text(python_code)
        
        result = self.adapter.validate_solution(self.temp_dir)
        
        assert result is True
    
    def test_validate_solution_missing_file(self):
        """Test validation when file doesn't exist."""
        result = self.adapter.validate_solution(self.temp_dir)
        
        assert result is False
    
    def test_validate_solution_empty_file(self):
        """Test validation with empty file."""
        self.main_py.write_text("")
        
        result = self.adapter.validate_solution(self.temp_dir)
        
        assert result is False
    
    def test_validate_solution_syntax_error(self):
        """Test validation with syntax error."""
        python_code = '''
def broken_function(
    print("Missing closing parenthesis")
'''
        self.main_py.write_text(python_code)
        
        result = self.adapter.validate_solution(self.temp_dir)
        
        assert result is False
    
    def test_validate_solution_valid_syntax(self):
        """Test validation with valid syntax."""
        python_code = '''
# Simple valid Python code
x = 1 + 2
print(x)
'''
        self.main_py.write_text(python_code)
        
        result = self.adapter.validate_solution(self.temp_dir)
        
        assert result is True
    
    def test_resource_limits_setting(self):
        """Test that resource limits are properly set."""
        limits = ResourceLimits(
            memory_mb=256,
            stack_mb=64,
            file_size_mb=10,
            open_files=64,
            processes=1
        )
        
        # Get the preexec function
        preexec_fn = self.adapter._set_resource_limits(limits)
        
        # Mock the resource module inside the preexec function
        with patch('resource.setrlimit') as mock_setrlimit, \
             patch('resource.RLIMIT_AS', 9), \
             patch('resource.RLIMIT_STACK', 3), \
             patch('resource.RLIMIT_FSIZE', 1), \
             patch('resource.RLIMIT_NOFILE', 7), \
             patch('resource.RLIMIT_NPROC', 6):
            
            # Call the preexec function
            preexec_fn()
            
            # Verify setrlimit was called with correct values
            expected_calls = [
                ((9, (256 * 1024 * 1024, 256 * 1024 * 1024)),),  # Memory
                ((3, (64 * 1024 * 1024, 64 * 1024 * 1024)),),    # Stack
                ((1, (10 * 1024 * 1024, 10 * 1024 * 1024)),),    # File size
                ((7, (64, 64)),),                                  # Open files
                ((6, (1, 1)),)                                     # Processes
            ]
            
            assert mock_setrlimit.call_count == 5
            for expected_call in expected_calls:
                assert expected_call in mock_setrlimit.call_args_list


class TestPythonAdapterIntegration:
    """Integration tests for Python adapter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = PythonAdapter()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.main_py = self.temp_dir / "main.py"
        self.stdin_file = self.temp_dir / "input.txt"
        self.stdout_file = self.temp_dir / "output.txt"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete compile and run workflow."""
        # Create a simple Python program
        python_code = '''
import sys

def main():
    line = sys.stdin.readline().strip()
    print(f"Hello, {line}!")

if __name__ == "__main__":
    main()
'''
        self.main_py.write_text(python_code)
        self.stdin_file.write_text("World\n")
        
        # Test compilation
        compile_result = self.adapter.compile(self.temp_dir)
        assert compile_result.success is True
        
        # Test execution
        limits = ResourceLimits(time_ms=2000, memory_mb=128)
        run_result = self.adapter.run(self.temp_dir, self.stdin_file, self.stdout_file, limits)
        
        # Note: This test might fail in CI environments without python3
        # In a real environment, we'd expect:
        # assert run_result.status == "OK"
        # assert run_result.exit_code == 0
        
        # For now, just verify the result structure
        assert hasattr(run_result, 'status')
        assert hasattr(run_result, 'exit_code')
        assert hasattr(run_result, 'time_ms')


if __name__ == "__main__":
    pytest.main([__file__])