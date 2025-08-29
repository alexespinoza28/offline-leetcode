#!/usr/bin/env python3
"""
Integration tests for the CLI run command handler.

Tests the complete workflow from CLI input to execution service integration.
"""

import json
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

try:
    from orchestrator.cli import OrchestatorCLI, CLIError
    from orchestrator.execution.service import ExecutionService
    from orchestrator.execution.executor import ExecutionStatus, TestCase, ExecutionResult, TestCaseResult
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from cli import OrchestatorCLI, CLIError
    from execution.service import ExecutionService
    from execution.executor import ExecutionStatus, TestCase, ExecutionResult, TestCaseResult


class TestCLIRunCommandIntegration:
    """Integration tests for the run command handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = OrchestatorCLI()
    
    @pytest.mark.asyncio
    async def test_run_command_python_success(self):
        """Test successful Python code execution."""
        # Mock the execution service
        mock_result = {
            "status": "accepted",
            "overall_result": "OK",
            "passed_tests": 2,
            "total_tests": 2,
            "success_rate": 100.0,
            "total_time_ms": 150,
            "average_time_ms": 75,
            "execution_id": "test-exec-123",
            "message": "All 2 test cases passed! ✅",
            "test_results": [
                {
                    "test_id": "test_1",
                    "status": "OK",
                    "input": "[2,7,11,15]\\n9",
                    "expected_output": "[0,1]",
                    "actual_output": "[0,1]",
                    "error": "",
                    "time_ms": 70,
                    "memory_mb": 12.5,
                    "diff": None,
                    "passed": True
                },
                {
                    "test_id": "test_2",
                    "status": "OK",
                    "input": "[3,2,4]\\n6",
                    "expected_output": "[1,2]",
                    "actual_output": "[1,2]",
                    "error": "",
                    "time_ms": 80,
                    "memory_mb": 13.2,
                    "diff": None,
                    "passed": True
                }
            ],
            "logs": {
                "compile": "",
                "stderr": ""
            }
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            # Create mock args
            args = Mock()
            args.problem = "two-sum"
            args.lang = "python"
            args.code = """
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
            args.code_file = None
            args.tests = "all"
            
            result = await self.cli.handle_run_command(args)
            
            # Verify result structure
            assert result["status"] == "success"
            assert result["command"] == "run"
            assert "result" in result
            
            cli_result = result["result"]
            assert cli_result["status"] == "OK"
            assert cli_result["summary"]["passed"] == 2
            assert cli_result["summary"]["total"] == 2
            assert cli_result["summary"]["total_time"] == 150
            assert len(cli_result["cases"]) == 2
            
            # Verify test case details
            case1 = cli_result["cases"][0]
            assert case1["test_id"] == "test_1"
            assert case1["status"] == "PASS"
            assert case1["time"] == 70
            assert case1["memory"] == 12.5
            
            # Verify service was called correctly
            mock_execute.assert_called_once_with(
                code=args.code,
                language="py",
                problem_id="two-sum",
                user_id=None,
                session_id=None
            )
    
    @pytest.mark.asyncio
    async def test_run_command_cpp_compilation_error(self):
        """Test C++ code with compilation error."""
        mock_result = {
            "status": "error",
            "message": "Compilation failed. Please check your syntax.",
            "logs": {
                "compile": "main.cpp:5:1: error: expected ';' before '}' token",
                "stderr": ""
            }
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            args = Mock()
            args.problem = "hello-world"
            args.lang = "cpp"
            args.code = """
#include <iostream>
int main() {
    std::cout << "Hello World" << std::endl
    return 0;
}
"""
            args.code_file = None
            args.tests = "all"
            
            result = await self.cli.handle_run_command(args)
            
            # Verify error handling
            assert result["status"] == "error"
            assert result["command"] == "run"
            assert "Compilation failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_run_command_wrong_answer(self):
        """Test code that produces wrong answers."""
        mock_result = {
            "status": "wrong_answer",
            "overall_result": "WA",
            "passed_tests": 1,
            "total_tests": 3,
            "success_rate": 33.3,
            "total_time_ms": 200,
            "execution_id": "test-exec-456",
            "message": "1/3 test cases passed. Check your logic.",
            "test_results": [
                {
                    "test_id": "test_1",
                    "status": "OK",
                    "input": "5",
                    "expected_output": "120",
                    "actual_output": "120",
                    "error": "",
                    "time_ms": 50,
                    "memory_mb": 8.1,
                    "diff": None,
                    "passed": True
                },
                {
                    "test_id": "test_2",
                    "status": "WA",
                    "input": "0",
                    "expected_output": "1",
                    "actual_output": "0",
                    "error": "",
                    "time_ms": 45,
                    "memory_mb": 8.0,
                    "diff": "Expected: 1\\nActual: 0",
                    "passed": False
                },
                {
                    "test_id": "test_3",
                    "status": "WA",
                    "input": "10",
                    "expected_output": "3628800",
                    "actual_output": "0",
                    "error": "",
                    "time_ms": 105,
                    "memory_mb": 8.2,
                    "diff": "Expected: 3628800\\nActual: 0",
                    "passed": False
                }
            ]
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            args = Mock()
            args.problem = "factorial"
            args.lang = "python"
            args.code = """
def factorial(n):
    if n <= 1:
        return 0  # Bug: should return 1
    return n * factorial(n - 1)
"""
            args.code_file = None
            args.tests = "all"
            
            result = await self.cli.handle_run_command(args)
            
            # Verify partial success handling
            assert result["status"] == "success"
            cli_result = result["result"]
            assert cli_result["status"] == "WA"
            assert cli_result["summary"]["passed"] == 1
            assert cli_result["summary"]["total"] == 3
            assert cli_result["summary"]["success_rate"] == 33.3
            
            # Verify failed test cases have diff information
            failed_cases = [case for case in cli_result["cases"] if case["status"] == "FAIL"]
            assert len(failed_cases) == 2
            assert failed_cases[0]["diff"] == "Expected: 1\\nActual: 0"
    
    @pytest.mark.asyncio
    async def test_run_command_timeout(self):
        """Test code that exceeds time limit."""
        mock_result = {
            "status": "time_limit_exceeded",
            "overall_result": "TLE",
            "passed_tests": 0,
            "total_tests": 1,
            "success_rate": 0.0,
            "total_time_ms": 2000,
            "execution_id": "test-exec-789",
            "message": "Time limit exceeded. Your solution is too slow.",
            "test_results": [
                {
                    "test_id": "test_1",
                    "status": "TLE",
                    "input": "1000000",
                    "expected_output": "...",
                    "actual_output": "",
                    "error": "Time limit exceeded (2.0s)",
                    "time_ms": 2000,
                    "memory_mb": 15.0,
                    "diff": None,
                    "passed": False
                }
            ]
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            args = Mock()
            args.problem = "fibonacci"
            args.lang = "python"
            args.code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Inefficient recursive solution
"""
            args.code_file = None
            args.tests = "all"
            
            result = await self.cli.handle_run_command(args)
            
            # Verify timeout handling
            assert result["status"] == "success"
            cli_result = result["result"]
            assert cli_result["status"] == "TLE"
            assert cli_result["summary"]["passed"] == 0
            assert cli_result["summary"]["total"] == 1
            
            # Verify timeout case details
            timeout_case = cli_result["cases"][0]
            assert timeout_case["status"] == "FAIL"
            assert "Time limit exceeded" in timeout_case["error"]
            assert timeout_case["time"] == 2000
    
    @pytest.mark.asyncio
    async def test_run_command_with_code_file(self):
        """Test run command with code loaded from file."""
        # Create temporary code file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def isPalindrome(s):
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
""")
            temp_path = f.name
        
        try:
            mock_result = {
                "status": "accepted",
                "overall_result": "OK",
                "passed_tests": 1,
                "total_tests": 1,
                "success_rate": 100.0,
                "total_time_ms": 85,
                "execution_id": "test-exec-file",
                "message": "All 1 test cases passed! ✅",
                "test_results": [
                    {
                        "test_id": "test_1",
                        "status": "OK",
                        "input": "A man a plan a canal Panama",
                        "expected_output": "true",
                        "actual_output": "true",
                        "error": "",
                        "time_ms": 85,
                        "memory_mb": 9.8,
                        "diff": None,
                        "passed": True
                    }
                ]
            }
            
            with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = mock_result
                
                args = Mock()
                args.problem = "valid-palindrome"
                args.lang = "python"
                args.code = None
                args.code_file = temp_path
                args.tests = "sample"
                
                result = await self.cli.handle_run_command(args)
                
                # Verify file loading worked
                assert result["status"] == "success"
                
                # Verify the code was loaded from file
                call_args = mock_execute.call_args
                assert "isPalindrome" in call_args[1]["code"]
                assert "cleaned" in call_args[1]["code"]
        
        finally:
            Path(temp_path).unlink()
    
    @pytest.mark.asyncio
    async def test_run_command_language_mapping(self):
        """Test language name mapping from CLI to execution service."""
        test_cases = [
            ("python", "py"),
            ("cpp", "cpp"),
            ("c", "c"),
            ("javascript", "js"),
            ("java", "java"),
            ("Python", "py"),  # Case insensitive
            ("C++", "cpp"),
            ("JavaScript", "js")
        ]
        
        mock_result = {
            "status": "accepted",
            "overall_result": "OK",
            "passed_tests": 1,
            "total_tests": 1,
            "test_results": []
        }
        
        for cli_lang, expected_exec_lang in test_cases:
            with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = mock_result
                
                args = Mock()
                args.problem = "test"
                args.lang = cli_lang
                args.code = "// test code"
                args.code_file = None
                args.tests = "all"
                
                await self.cli.handle_run_command(args)
                
                # Verify correct language mapping
                call_args = mock_execute.call_args
                assert call_args[1]["language"] == expected_exec_lang
    
    @pytest.mark.asyncio
    async def test_run_command_json_input(self):
        """Test run command with JSON input."""
        mock_result = {
            "status": "accepted",
            "overall_result": "OK",
            "passed_tests": 1,
            "total_tests": 1,
            "test_results": []
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            args = Mock()
            args.problem = None
            args.lang = None
            args.code = None
            args.code_file = None
            args.tests = "all"
            
            json_data = {
                "problem": "reverse-string",
                "lang": "cpp",
                "code": "void reverseString(vector<char>& s) { reverse(s.begin(), s.end()); }",
                "tests": "unit"
            }
            
            result = await self.cli.handle_run_command(args, json_data)
            
            # Verify JSON data was used
            assert result["status"] == "success"
            
            call_args = mock_execute.call_args
            assert call_args[1]["problem_id"] == "reverse-string"
            assert call_args[1]["language"] == "cpp"
            assert "reverseString" in call_args[1]["code"]
    
    @pytest.mark.asyncio
    async def test_run_command_execution_service_exception(self):
        """Test handling of execution service exceptions."""
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Database connection failed")
            
            args = Mock()
            args.problem = "test"
            args.lang = "python"
            args.code = "print('hello')"
            args.code_file = None
            args.tests = "all"
            
            result = await self.cli.handle_run_command(args)
            
            # Verify exception handling
            assert result["status"] == "error"
            assert result["command"] == "run"
            assert "Execution failed" in result["error"]
            assert "Database connection failed" in result["error"]
    
    def test_run_command_no_code_provided(self):
        """Test error when no code is provided."""
        args = Mock()
        args.problem = "test"
        args.lang = "python"
        args.code = None
        args.code_file = None
        args.tests = "all"
        
        # This should be synchronous since it fails before async execution
        with pytest.raises(CLIError, match="No source code provided"):
            asyncio.run(self.cli.handle_run_command(args))


class TestCLIRunCommandEndToEnd:
    """End-to-end tests for the complete CLI run workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = OrchestatorCLI()
    
    def test_run_command_full_workflow_json_output(self):
        """Test complete workflow with JSON output."""
        # Mock the execution service for end-to-end test
        mock_result = {
            "status": "accepted",
            "overall_result": "OK",
            "passed_tests": 1,
            "total_tests": 1,
            "success_rate": 100.0,
            "total_time_ms": 95,
            "execution_id": "e2e-test",
            "message": "All tests passed!",
            "test_results": [
                {
                    "test_id": "test_1",
                    "status": "OK",
                    "input": "hello",
                    "expected_output": "HELLO",
                    "actual_output": "HELLO",
                    "error": "",
                    "time_ms": 95,
                    "memory_mb": 7.5,
                    "diff": None,
                    "passed": True
                }
            ]
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            # Test complete CLI workflow
            exit_code = self.cli.run([
                '--json-output',
                'run',
                '--problem', 'to-upper-case',
                '--lang', 'python',
                '--code', 'def toUpperCase(s): return s.upper()'
            ])
            
            assert exit_code == 0
            mock_execute.assert_called_once()
    
    def test_run_command_full_workflow_human_readable(self):
        """Test complete workflow with human-readable output."""
        mock_result = {
            "status": "wrong_answer",
            "overall_result": "WA",
            "passed_tests": 2,
            "total_tests": 3,
            "success_rate": 66.7,
            "total_time_ms": 180,
            "execution_id": "e2e-test-2",
            "message": "2/3 test cases passed",
            "test_results": [
                {
                    "test_id": "test_1",
                    "status": "OK",
                    "passed": True,
                    "time_ms": 60
                },
                {
                    "test_id": "test_2",
                    "status": "OK", 
                    "passed": True,
                    "time_ms": 55
                },
                {
                    "test_id": "test_3",
                    "status": "WA",
                    "passed": False,
                    "time_ms": 65
                }
            ]
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            with patch('builtins.print') as mock_print:
                exit_code = self.cli.run([
                    'run',
                    '--problem', 'array-sum',
                    '--lang', 'java',
                    '--code', 'public int sum(int[] arr) { return 0; }'  # Buggy implementation
                ])
                
                assert exit_code == 0  # CLI succeeds even with wrong answer
                
                # Verify human-readable output was printed
                printed_output = ' '.join(call[0][0] for call in mock_print.call_args_list)
                assert "✅ Run completed successfully" in printed_output
                assert "Tests: 2/3 passed" in printed_output
                assert "Time: 180ms" in printed_output


if __name__ == "__main__":
    pytest.main([__file__])