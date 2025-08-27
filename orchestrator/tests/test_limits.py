"""
Unit tests for resource limit utilities.

This module tests the resource limit enforcement system used for
secure code execution with proper isolation and constraint enforcement.
"""

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from orchestrator.utils.limits import (
    ResourceLimits, ExecutionResult, ResourceLimitEnforcer,
    create_secure_temp_dir, cleanup_temp_dir
)


class TestResourceLimits(unittest.TestCase):
    """Test cases for ResourceLimits dataclass."""
    
    def test_default_limits(self):
        """Test default resource limit values."""
        limits = ResourceLimits()
        
        self.assertEqual(limits.time_ms, 2000)
        self.assertEqual(limits.cpu_time_ms, 2000)
        self.assertEqual(limits.memory_mb, 256)
        self.assertEqual(limits.stack_mb, 64)
        self.assertEqual(limits.file_size_mb, 10)
        self.assertEqual(limits.open_files, 64)
        self.assertEqual(limits.processes, 1)
    
    def test_custom_limits(self):
        """Test creating ResourceLimits with custom values."""
        limits = ResourceLimits(
            time_ms=5000,
            memory_mb=512,
            processes=2
        )
        
        self.assertEqual(limits.time_ms, 5000)
        self.assertEqual(limits.memory_mb, 512)
        self.assertEqual(limits.processes, 2)
        # Other values should remain default
        self.assertEqual(limits.cpu_time_ms, 2000)
        self.assertEqual(limits.stack_mb, 64)
    
    def test_invalid_limits_validation(self):
        """Test validation of invalid resource limit values."""
        invalid_values = [
            {"time_ms": 0},
            {"time_ms": -1000},
            {"memory_mb": 0},
            {"memory_mb": -256},
            {"cpu_time_ms": -1},
            {"stack_mb": 0},
            {"file_size_mb": -1},
            {"open_files": 0},
            {"processes": -1}
        ]
        
        for invalid_kwargs in invalid_values:
            with self.subTest(kwargs=invalid_kwargs):
                with self.assertRaises(ValueError):
                    ResourceLimits(**invalid_kwargs)
    
    def test_from_problem_config_defaults(self):
        """Test creating limits from problem config with defaults."""
        problem_data = {"title": "Test Problem"}
        limits = ResourceLimits.from_problem_config(problem_data)
        
        # Should use default values
        self.assertEqual(limits.time_ms, 2000)
        self.assertEqual(limits.memory_mb, 256)
    
    def test_from_problem_config_with_limits(self):
        """Test creating limits from problem config with specified limits."""
        problem_data = {
            "title": "Test Problem",
            "limits": {
                "time_ms": 5000,
                "memory_mb": 512
            }
        }
        limits = ResourceLimits.from_problem_config(problem_data)
        
        # Should use problem-specific values
        self.assertEqual(limits.time_ms, 5000)
        self.assertEqual(limits.memory_mb, 512)
        # Others should remain default
        self.assertEqual(limits.cpu_time_ms, 2000)
    
    def test_from_problem_config_with_overrides(self):
        """Test creating limits with user overrides."""
        problem_data = {
            "limits": {"time_ms": 3000, "memory_mb": 256}
        }
        overrides = {"time_ms": 10000, "processes": 2}
        
        limits = ResourceLimits.from_problem_config(problem_data, overrides)
        
        # Overrides should take precedence
        self.assertEqual(limits.time_ms, 10000)
        self.assertEqual(limits.processes, 2)
        # Problem config should be used where no override
        self.assertEqual(limits.memory_mb, 256)
    
    def test_to_dict(self):
        """Test converting ResourceLimits to dictionary."""
        limits = ResourceLimits(time_ms=5000, memory_mb=512)
        result = limits.to_dict()
        
        expected = {
            "time_ms": 5000,
            "cpu_time_ms": 2000,
            "memory_mb": 512,
            "stack_mb": 64,
            "file_size_mb": 10,
            "open_files": 64,
            "processes": 1
        }
        
        self.assertEqual(result, expected)


class TestExecutionResult(unittest.TestCase):
    """Test cases for ExecutionResult dataclass."""
    
    def test_default_execution_result(self):
        """Test default ExecutionResult values."""
        result = ExecutionResult(status="OK")
        
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.time_ms)
        self.assertIsNone(result.memory_mb)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
        self.assertIsNone(result.signal)
        self.assertIsNone(result.killed_by_limit)
    
    def test_custom_execution_result(self):
        """Test ExecutionResult with custom values."""
        result = ExecutionResult(
            status="TIMEOUT",
            exit_code=-9,
            time_ms=2500,
            memory_mb=128,
            stdout="output",
            stderr="error",
            signal=9,
            killed_by_limit="wall_clock_timeout"
        )
        
        self.assertEqual(result.status, "TIMEOUT")
        self.assertEqual(result.exit_code, -9)
        self.assertEqual(result.time_ms, 2500)
        self.assertEqual(result.memory_mb, 128)
        self.assertEqual(result.stdout, "output")
        self.assertEqual(result.stderr, "error")
        self.assertEqual(result.signal, 9)
        self.assertEqual(result.killed_by_limit, "wall_clock_timeout")


class TestResourceLimitEnforcer(unittest.TestCase):
    """Test cases for ResourceLimitEnforcer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.limits = ResourceLimits(time_ms=1000, memory_mb=128)
        self.enforcer = ResourceLimitEnforcer(self.limits)
    
    def test_enforcer_initialization(self):
        """Test ResourceLimitEnforcer initialization."""
        self.assertEqual(self.enforcer.limits, self.limits)
        self.assertIsNone(self.enforcer._process)
        self.assertIsNone(self.enforcer._start_time)
        self.assertEqual(self.enforcer._peak_memory, 0)
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_successful_execution(self):
        """Test successful command execution."""
        result = self.enforcer.run_with_limits(["echo", "hello world"])
        
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), "hello world")
        self.assertEqual(result.stderr, "")
        self.assertIsNotNone(result.time_ms)
        self.assertGreater(result.time_ms, 0)
        self.assertLess(result.time_ms, 1000)  # Should be much faster than limit
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_command_with_stdin(self):
        """Test command execution with stdin input."""
        result = self.enforcer.run_with_limits(["cat"], stdin_data="test input")
        
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "test input")
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_command_with_working_directory(self):
        """Test command execution with specific working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")
            
            result = self.enforcer.run_with_limits(
                ["cat", "test.txt"],
                cwd=temp_path
            )
            
            self.assertEqual(result.status, "OK")
            self.assertEqual(result.stdout, "test content")
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_command_with_environment(self):
        """Test command execution with custom environment."""
        env = {"TEST_VAR": "test_value"}
        result = self.enforcer.run_with_limits(
            ["sh", "-c", "echo $TEST_VAR"],
            env=env
        )
        
        self.assertEqual(result.status, "OK")
        self.assertEqual(result.stdout.strip(), "test_value")
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_timeout_enforcement(self):
        """Test wall clock timeout enforcement."""
        # Use very short timeout
        short_limits = ResourceLimits(time_ms=100)
        enforcer = ResourceLimitEnforcer(short_limits)
        
        # Command that sleeps longer than timeout
        result = enforcer.run_with_limits(["sleep", "1"])
        
        self.assertEqual(result.status, "TIMEOUT")
        self.assertIsNotNone(result.time_ms)
        self.assertGreaterEqual(result.time_ms, 100)
        self.assertEqual(result.killed_by_limit, "wall_clock_timeout")
        self.assertIn("timeout", result.stderr.lower())
    
    def test_nonexistent_command(self):
        """Test execution of nonexistent command."""
        result = self.enforcer.run_with_limits(["nonexistent_command_12345"])
        
        self.assertEqual(result.status, "RE")
        self.assertIn("Failed to start process", result.stderr)
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_command_with_nonzero_exit(self):
        """Test command that exits with non-zero code."""
        result = self.enforcer.run_with_limits(["sh", "-c", "exit 42"])
        
        self.assertEqual(result.status, "RE")
        self.assertEqual(result.exit_code, 42)
    
    def test_determine_status_ok(self):
        """Test status determination for successful execution."""
        status = self.enforcer._determine_status(0, 500)
        self.assertEqual(status, "OK")
    
    def test_determine_status_runtime_error(self):
        """Test status determination for runtime errors."""
        status = self.enforcer._determine_status(1, 500)
        self.assertEqual(status, "RE")
        
        status = self.enforcer._determine_status(255, 500)
        self.assertEqual(status, "RE")
    
    @unittest.skipIf(os.name == 'nt', "Unix-specific test")
    def test_determine_status_signals(self):
        """Test status determination for signal-based termination."""
        import signal
        
        # CPU time limit exceeded
        status = self.enforcer._determine_status(-signal.SIGXCPU, 500)
        self.assertEqual(status, "TLE")
        
        # Killed (likely memory limit)
        status = self.enforcer._determine_status(-signal.SIGKILL, 500)
        self.assertEqual(status, "MLE")
        
        # File size limit exceeded
        status = self.enforcer._determine_status(-signal.SIGXFSZ, 500)
        self.assertEqual(status, "OLE")


class TestTempDirectoryUtils(unittest.TestCase):
    """Test cases for temporary directory utilities."""
    
    def test_create_secure_temp_dir(self):
        """Test creation of secure temporary directory."""
        temp_dir = create_secure_temp_dir()
        
        try:
            self.assertTrue(temp_dir.exists())
            self.assertTrue(temp_dir.is_dir())
            
            # Check permissions (Unix only)
            if os.name != 'nt':
                stat_info = temp_dir.stat()
                permissions = oct(stat_info.st_mode)[-3:]
                self.assertEqual(permissions, '700')  # Owner only
        finally:
            cleanup_temp_dir(temp_dir)
    
    def test_create_temp_dir_with_base(self):
        """Test creation of temporary directory with custom base."""
        with tempfile.TemporaryDirectory() as base_dir:
            base_path = Path(base_dir)
            temp_dir = create_secure_temp_dir(base_path)
            
            try:
                self.assertTrue(temp_dir.exists())
                self.assertTrue(temp_dir.is_dir())
                # Should be created within base directory
                self.assertTrue(str(temp_dir).startswith(str(base_path)))
            finally:
                cleanup_temp_dir(temp_dir)
    
    def test_cleanup_temp_dir(self):
        """Test cleanup of temporary directory."""
        temp_dir = create_secure_temp_dir()
        
        # Create some files in the directory
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Create subdirectory
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "nested.txt").write_text("nested content")
        
        # Verify directory exists and has content
        self.assertTrue(temp_dir.exists())
        self.assertTrue(test_file.exists())
        self.assertTrue(sub_dir.exists())
        
        # Clean up
        cleanup_temp_dir(temp_dir)
        
        # Verify directory is gone
        self.assertFalse(temp_dir.exists())
    
    def test_cleanup_nonexistent_dir(self):
        """Test cleanup of nonexistent directory doesn't raise error."""
        nonexistent_dir = Path("/nonexistent/directory/path")
        
        # Should not raise an exception
        cleanup_temp_dir(nonexistent_dir)
    
    def test_cleanup_file_instead_of_dir(self):
        """Test cleanup when path points to file instead of directory."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # Should not raise an exception
            cleanup_temp_dir(temp_path)
            # File should still exist (we only clean directories)
            self.assertTrue(temp_path.exists())
        finally:
            temp_path.unlink()


if __name__ == '__main__':
    unittest.main()