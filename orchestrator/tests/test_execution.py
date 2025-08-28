import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from ..execution.executor import CodeExecutor, TestCase, ExecutionStatus
from ..execution.service import ExecutionService

class TestCodeExecutor:
    """Test cases for the CodeExecutor class."""
    
    @pytest.fixture
    def executor(self):
        """Create a temporary executor for testing."""
        temp_dir = tempfile.mkdtemp()
        executor = CodeExecutor(work_dir=temp_dir)
        yield executor
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_python_execution_success(self, executor):
        """Test successful Python code execution."""
        code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

# Read input
import sys
lines = sys.stdin.read().strip().split('\\n')
nums = eval(lines[0])
target = int(lines[1])
result = two_sum(nums, target)
print(result)
"""
        
        test_cases = [
            TestCase(
                id="test_1",
                input_data="[2,7,11,15]\\n9",
                expected_output="[0, 1]",
                time_limit=2.0
            )
        ]
        
        status, results, logs = await executor.execute_code(
            code=code,
            language="py",
            test_cases=test_cases
        )
        
        assert status == ExecutionStatus.OK
        assert len(results) == 1
        assert results[0].result.status == ExecutionStatus.OK
    
    @pytest.mark.asyncio
    async def test_python_syntax_error(self, executor):
        """Test Python syntax error handling."""
        code = """
def invalid_syntax(
    print("Missing closing parenthesis")
"""
        
        test_cases = [
            TestCase(
                id="test_1",
                input_data="",
                expected_output="",
                time_limit=1.0
            )
        ]
        
        status, results, logs = await executor.execute_code(
            code=code,
            language="py",
            test_cases=test_cases
        )
        
        # Python doesn't compile, so this should be a runtime error
        assert status in [ExecutionStatus.RE, ExecutionStatus.CE]
    
    @pytest.mark.asyncio
    async def test_python_timeout(self, executor):
        """Test timeout handling."""
        code = """
import time
time.sleep(5)  # Sleep longer than timeout
print("This should not print")
"""
        
        test_cases = [
            TestCase(
                id="test_1",
                input_data="",
                expected_output="",
                time_limit=1.0  # 1 second timeout
            )
        ]
        
        status, results, logs = await executor.execute_code(
            code=code,
            language="py",
            test_cases=test_cases
        )
        
        assert status == ExecutionStatus.TLE
        assert len(results) == 1
        assert results[0].result.status == ExecutionStatus.TLE
    
    @pytest.mark.asyncio
    async def test_wrong_answer(self, executor):
        """Test wrong answer detection."""
        code = """
print("wrong answer")
"""
        
        test_cases = [
            TestCase(
                id="test_1",
                input_data="",
                expected_output="correct answer",
                time_limit=1.0
            )
        ]
        
        status, results, logs = await executor.execute_code(
            code=code,
            language="py",
            test_cases=test_cases
        )
        
        assert status == ExecutionStatus.WA
        assert len(results) == 1
        assert results[0].result.status == ExecutionStatus.WA
        assert results[0].diff is not None
    
    @pytest.mark.asyncio
    async def test_cpp_compilation_success(self, executor):
        """Test C++ compilation and execution."""
        code = """
#include <iostream>
#include <vector>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
"""
        
        test_cases = [
            TestCase(
                id="test_1",
                input_data="",
                expected_output="Hello, World!",
                time_limit=1.0
            )
        ]
        
        status, results, logs = await executor.execute_code(
            code=code,
            language="cpp",
            test_cases=test_cases
        )
        
        assert status == ExecutionStatus.OK
        assert len(results) == 1
        assert results[0].result.status == ExecutionStatus.OK
    
    @pytest.mark.asyncio
    async def test_cpp_compilation_error(self, executor):
        """Test C++ compilation error handling."""
        code = """
#include <iostream>
using namespace std;

int main() {
    cout << "Missing semicolon"  // Syntax error
    return 0;
}
"""
        
        test_cases = [
            TestCase(
                id="test_1",
                input_data="",
                expected_output="",
                time_limit=1.0
            )
        ]
        
        status, results, logs = await executor.execute_code(
            code=code,
            language="cpp",
            test_cases=test_cases
        )
        
        assert status == ExecutionStatus.CE
        assert "compile" in logs or "stderr" in logs
    
    @pytest.mark.asyncio
    async def test_javascript_execution(self, executor):
        """Test JavaScript execution."""
        code = """
console.log("Hello from Node.js!");
"""
        
        test_cases = [
            TestCase(
                id="test_1",
                input_data="",
                expected_output="Hello from Node.js!",
                time_limit=1.0
            )
        ]
        
        status, results, logs = await executor.execute_code(
            code=code,
            language="js",
            test_cases=test_cases
        )
        
        assert status == ExecutionStatus.OK
        assert len(results) == 1
        assert results[0].result.status == ExecutionStatus.OK
    
    @pytest.mark.asyncio
    async def test_syntax_validation_python(self, executor):
        """Test Python syntax validation."""
        valid_code = "print('Hello, World!')"
        invalid_code = "print('Missing quote)"
        
        is_valid, message = await executor.validate_code_syntax(valid_code, "py")
        assert is_valid is True
        
        is_valid, message = await executor.validate_code_syntax(invalid_code, "py")
        assert is_valid is False
        assert "syntax" in message.lower() or "error" in message.lower()


class TestExecutionService:
    """Test cases for the ExecutionService class."""
    
    @pytest.fixture
    def service(self):
        """Create a temporary execution service for testing."""
        temp_dir = tempfile.mkdtemp()
        service = ExecutionService(work_dir=temp_dir)
        yield service
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_execute_solution_success(self, service):
        """Test successful solution execution."""
        code = """
def solution():
    return "Hello, World!"

print(solution())
"""
        
        result = await service.execute_solution(
            code=code,
            language="py",
            problem_id="test-problem"
        )
        
        assert result["status"] != "error"
        assert "execution_id" in result
        assert "test_results" in result
    
    @pytest.mark.asyncio
    async def test_validate_syntax_service(self, service):
        """Test syntax validation through service."""
        result = await service.validate_syntax(
            code="print('Hello')",
            language="py"
        )
        
        assert result["valid"] is True
        assert result["language"] == "py"
    
    @pytest.mark.asyncio
    async def test_get_execution_stats(self, service):
        """Test execution statistics retrieval."""
        stats = await service.get_execution_stats()
        
        assert "total_executions" in stats
        assert "successful_executions" in stats
        assert "failed_executions" in stats
        assert "avg_execution_time" in stats


if __name__ == "__main__":
    pytest.main([__file__])