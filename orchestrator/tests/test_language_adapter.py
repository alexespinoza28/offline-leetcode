"""
Unit tests for LanguageAdapter base interface.

Tests the abstract base class contract and data structures used by all language adapters.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from orchestrator.language_adapters import LanguageAdapter, CompileResult, RunResult, ResourceLimits


class MockLanguageAdapter(LanguageAdapter):
    """Mock implementation of LanguageAdapter for testing."""
    
    def __init__(self):
        super().__init__()
        self.name = "mock"
        self.entry_file = "main.mock"
        self.runtime_cmd = ["mock", "main.mock"]
    
    def compile(self, workdir: Path) -> CompileResult:
        return CompileResult(success=True, stdout="Mock compilation successful")
    
    def run(self, workdir: Path, stdin_path: Path, stdout_path: Path, 
            limits: ResourceLimits) -> RunResult:
        return RunResult(status="OK", time_ms=100, memory_mb=10)


class TestResourceLimits:
    """Test ResourceLimits data structure."""
    
    def test_default_values(self):
        """Test that ResourceLimits has correct default values."""
        limits = ResourceLimits()
        
        assert limits.time_ms == 2000
        assert limits.cpu_time_ms == 2000
        assert limits.memory_mb == 256
        assert limits.stack_mb == 64
        assert limits.file_size_mb == 10
        assert limits.open_files == 64
        assert limits.processes == 1
    
    def test_custom_values(self):
        """Test ResourceLimits with custom values."""
        limits = ResourceLimits(
            time_ms=5000,
            memory_mb=512,
            processes=2
        )
        
        assert limits.time_ms == 5000
        assert limits.memory_mb == 512
        assert limits.processes == 2
        # Other values should remain default
        assert limits.cpu_time_ms == 2000
        assert limits.stack_mb == 64


class TestCompileResult:
    """Test CompileResult data structure."""
    
    def test_successful_compilation(self):
        """Test CompileResult for successful compilation."""
        result = CompileResult(
            success=True,
            stdout="Compilation successful",
            stderr="",
            exit_code=0,
            compile_time_ms=150
        )
        
        assert result.success is True
        assert result.stdout == "Compilation successful"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.compile_time_ms == 150
    
    def test_failed_compilation(self):
        """Test CompileResult for failed compilation."""
        result = CompileResult(
            success=False,
            stdout="",
            stderr="error: expected ';' before '}' token",
            exit_code=1,
            compile_time_ms=50
        )
        
        assert result.success is False
        assert result.stderr == "error: expected ';' before '}' token"
        assert result.exit_code == 1
        assert result.compile_time_ms == 50
    
    def test_default_values(self):
        """Test CompileResult default values."""
        result = CompileResult(success=True)
        
        assert result.success is True
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.compile_time_ms is None


class TestRunResult:
    """Test RunResult data structure."""
    
    def test_successful_execution(self):
        """Test RunResult for successful execution."""
        result = RunResult(
            status="OK",
            exit_code=0,
            time_ms=250,
            memory_mb=15,
            stdout="Hello, World!",
            stderr=""
        )
        
        assert result.status == "OK"
        assert result.exit_code == 0
        assert result.time_ms == 250
        assert result.memory_mb == 15
        assert result.stdout == "Hello, World!"
        assert result.stderr == ""
        assert result.signal is None
    
    def test_timeout_execution(self):
        """Test RunResult for timeout."""
        result = RunResult(
            status="TIMEOUT",
            exit_code=124,
            time_ms=2000,
            memory_mb=50,
            signal=9
        )
        
        assert result.status == "TIMEOUT"
        assert result.exit_code == 124
        assert result.time_ms == 2000
        assert result.signal == 9
    
    def test_memory_limit_exceeded(self):
        """Test RunResult for memory limit exceeded."""
        result = RunResult(
            status="MLE",
            exit_code=137,
            memory_mb=256,
            signal=9
        )
        
        assert result.status == "MLE"
        assert result.exit_code == 137
        assert result.memory_mb == 256
        assert result.signal == 9
    
    def test_runtime_error(self):
        """Test RunResult for runtime error."""
        result = RunResult(
            status="RE",
            exit_code=139,
            stderr="Segmentation fault (core dumped)",
            signal=11
        )
        
        assert result.status == "RE"
        assert result.exit_code == 139
        assert result.stderr == "Segmentation fault (core dumped)"
        assert result.signal == 11


class TestLanguageAdapter:
    """Test LanguageAdapter abstract base class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that LanguageAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LanguageAdapter()
    
    def test_mock_adapter_initialization(self):
        """Test that mock adapter initializes correctly."""
        adapter = MockLanguageAdapter()
        
        assert adapter.name == "mock"
        assert adapter.entry_file == "main.mock"
        assert adapter.runtime_cmd == ["mock", "main.mock"]
    
    def test_compile_method_contract(self):
        """Test that compile method follows the expected contract."""
        adapter = MockLanguageAdapter()
        workdir = Path("/tmp/test")
        
        result = adapter.compile(workdir)
        
        assert isinstance(result, CompileResult)
        assert result.success is True
        assert isinstance(result.stdout, str)
        assert isinstance(result.stderr, str)
        assert isinstance(result.exit_code, int)
    
    def test_run_method_contract(self):
        """Test that run method follows the expected contract."""
        adapter = MockLanguageAdapter()
        workdir = Path("/tmp/test")
        stdin_path = Path("/tmp/input.txt")
        stdout_path = Path("/tmp/output.txt")
        limits = ResourceLimits()
        
        result = adapter.run(workdir, stdin_path, stdout_path, limits)
        
        assert isinstance(result, RunResult)
        assert isinstance(result.status, str)
        assert isinstance(result.exit_code, int)
        assert result.time_ms is None or isinstance(result.time_ms, int)
        assert result.memory_mb is None or isinstance(result.memory_mb, int)
        assert isinstance(result.stdout, str)
        assert isinstance(result.stderr, str)
        assert result.signal is None or isinstance(result.signal, int)
    
    def test_get_template_content_default(self):
        """Test default template content method."""
        adapter = MockLanguageAdapter()
        
        template = adapter.get_template_content()
        
        assert isinstance(template, str)
        assert template == ""  # Default implementation returns empty string
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_validate_solution_success(self, mock_is_file, mock_exists):
        """Test successful solution validation."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        adapter = MockLanguageAdapter()
        workdir = Path("/tmp/test")
        
        result = adapter.validate_solution(workdir)
        
        assert result is True
        mock_exists.assert_called_once()
        mock_is_file.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_validate_solution_file_not_exists(self, mock_exists):
        """Test solution validation when file doesn't exist."""
        mock_exists.return_value = False
        
        adapter = MockLanguageAdapter()
        workdir = Path("/tmp/test")
        
        result = adapter.validate_solution(workdir)
        
        assert result is False
        mock_exists.assert_called_once()
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_validate_solution_not_file(self, mock_is_file, mock_exists):
        """Test solution validation when path exists but is not a file."""
        mock_exists.return_value = True
        mock_is_file.return_value = False
        
        adapter = MockLanguageAdapter()
        workdir = Path("/tmp/test")
        
        result = adapter.validate_solution(workdir)
        
        assert result is False
        mock_exists.assert_called_once()
        mock_is_file.assert_called_once()


class TestLanguageAdapterIntegration:
    """Integration tests for LanguageAdapter interface."""
    
    def test_complete_workflow_simulation(self):
        """Test a complete compile and run workflow."""
        adapter = MockLanguageAdapter()
        workdir = Path("/tmp/test")
        stdin_path = Path("/tmp/input.txt")
        stdout_path = Path("/tmp/output.txt")
        limits = ResourceLimits(time_ms=1000, memory_mb=128)
        
        # Test compilation
        compile_result = adapter.compile(workdir)
        assert compile_result.success is True
        
        # Test execution
        run_result = adapter.run(workdir, stdin_path, stdout_path, limits)
        assert run_result.status == "OK"
        assert run_result.time_ms == 100
        assert run_result.memory_mb == 10
    
    def test_resource_limits_propagation(self):
        """Test that resource limits are properly passed to run method."""
        adapter = MockLanguageAdapter()
        workdir = Path("/tmp/test")
        stdin_path = Path("/tmp/input.txt")
        stdout_path = Path("/tmp/output.txt")
        
        # Test with custom limits
        custom_limits = ResourceLimits(
            time_ms=5000,
            memory_mb=512,
            processes=2
        )
        
        result = adapter.run(workdir, stdin_path, stdout_path, custom_limits)
        
        # Mock adapter should still return OK regardless of limits
        assert result.status == "OK"
        assert isinstance(result, RunResult)


if __name__ == "__main__":
    pytest.main([__file__])