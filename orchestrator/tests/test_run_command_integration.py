#!/usr/bin/env python3
"""
Integration tests specifically for the run command handler.

Tests the integration between CLI and execution service.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from orchestrator.cli import OrchestatorCLI, CLIError


class TestRunCommandIntegration:
    """Integration tests for the run command handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = OrchestatorCLI()
    
    @pytest.mark.asyncio
    async def test_run_command_successful_execution(self):
        """Test successful code execution through run command."""
        mock_result = {
            "status": "accepted",
            "overall_result": "OK",
            "passed_tests": 2,
            "total_tests": 2,
            "success_rate": 100.0,
            "total_time_ms": 120,
            "execution_id": "test-success",
            "message": "All 2 test cases passed! ✅",
            "test_results": [
                {
                    "test_id": "test_1",
                    "status": "OK",
                    "input": "[2,7,11,15]\\n9",
                    "expected_output": "[0,1]",
                    "actual_output": "[0,1]",
                    "error": "",
                    "time_ms": 60,
                    "memory_mb": 12.3,
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
                    "time_ms": 60,
                    "memory_mb": 12.1,
                    "diff": None,
                    "passed": True
                }
            ]
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
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
            
            # Verify successful result structure
            assert result["status"] == "success"
            assert result["command"] == "run"
            
            cli_result = result["result"]
            assert cli_result["status"] == "OK"
            assert cli_result["summary"]["passed"] == 2
            assert cli_result["summary"]["total"] == 2
            assert cli_result["summary"]["total_time"] == 120
            assert cli_result["summary"]["success_rate"] == 100.0
            assert len(cli_result["cases"]) == 2
            
            # Verify test case details
            case1 = cli_result["cases"][0]
            assert case1["test_id"] == "test_1"
            assert case1["status"] == "PASS"
            assert case1["time"] == 60
            assert case1["memory"] == 12.3
            assert case1["input"] == "[2,7,11,15]\\n9"
            assert case1["expected"] == "[0,1]"
            assert case1["actual"] == "[0,1]"
            assert case1["error"] == ""
            assert case1["diff"] is None
            
            # Verify execution service was called correctly
            mock_execute.assert_called_once_with(
                code=args.code,
                language="py",
                problem_id="two-sum",
                user_id=None,
                session_id=None
            )
    
    @pytest.mark.asyncio
    async def test_run_command_compilation_error(self):
        """Test handling of compilation errors."""
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
            
            # Verify service was called
            mock_execute.assert_called_once_with(
                code=args.code,
                language="cpp",
                problem_id="hello-world",
                user_id=None,
                session_id=None
            )
    
    @pytest.mark.asyncio
    async def test_run_command_wrong_answer(self):
        """Test handling of wrong answer results."""
        mock_result = {
            "status": "wrong_answer",
            "overall_result": "WA",
            "passed_tests": 1,
            "total_tests": 3,
            "success_rate": 33.3,
            "total_time_ms": 200,
            "execution_id": "test-wa",
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
            assert result["status"] == "success"  # CLI succeeds even with wrong answer
            
            cli_result = result["result"]
            assert cli_result["status"] == "WA"
            assert cli_result["summary"]["passed"] == 1
            assert cli_result["summary"]["total"] == 3
            assert cli_result["summary"]["success_rate"] == 33.3
            assert len(cli_result["cases"]) == 3
            
            # Verify failed test cases have diff information
            failed_cases = [case for case in cli_result["cases"] if case["status"] == "FAIL"]
            assert len(failed_cases) == 2
            assert failed_cases[0]["diff"] == "Expected: 1\\nActual: 0"
            assert failed_cases[1]["diff"] == "Expected: 3628800\\nActual: 0"
    
    @pytest.mark.asyncio
    async def test_run_command_timeout(self):
        """Test handling of timeout errors."""
        mock_result = {
            "status": "time_limit_exceeded",
            "overall_result": "TLE",
            "passed_tests": 0,
            "total_tests": 1,
            "success_rate": 0.0,
            "total_time_ms": 2000,
            "execution_id": "test-tle",
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
            assert result["status"] == "success"  # CLI succeeds even with timeout
            
            cli_result = result["result"]
            assert cli_result["status"] == "TLE"
            assert cli_result["summary"]["passed"] == 0
            assert cli_result["summary"]["total"] == 1
            assert cli_result["summary"]["success_rate"] == 0.0
            
            # Verify timeout case details
            timeout_case = cli_result["cases"][0]
            assert timeout_case["status"] == "FAIL"
            assert "Time limit exceeded" in timeout_case["error"]
            assert timeout_case["time"] == 2000
    
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
    async def test_run_command_json_input_override(self):
        """Test that JSON input overrides command-line arguments."""
        mock_result = {
            "status": "accepted",
            "overall_result": "OK",
            "passed_tests": 1,
            "total_tests": 1,
            "test_results": []
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            # Command-line args
            args = Mock()
            args.problem = "cli-problem"
            args.lang = "cli-lang"
            args.code = "cli code"
            args.code_file = None
            args.tests = "cli-tests"
            
            # JSON data should override
            json_data = {
                "problem": "json-problem",
                "lang": "cpp",
                "code": "json code",
                "tests": "sample"
            }
            
            result = await self.cli.handle_run_command(args, json_data)
            
            # Verify JSON data was used
            assert result["status"] == "success"
            
            call_args = mock_execute.call_args
            assert call_args[1]["problem_id"] == "json-problem"
            assert call_args[1]["language"] == "cpp"
            assert call_args[1]["code"] == "json code"
    
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
    
    @pytest.mark.asyncio
    async def test_run_command_no_code_provided(self):
        """Test error when no code is provided."""
        args = Mock()
        args.problem = "test"
        args.lang = "python"
        args.code = None
        args.code_file = None
        args.tests = "all"
        
        with pytest.raises(CLIError, match="No source code provided"):
            await self.cli.handle_run_command(args)


if __name__ == "__main__":
    pytest.main([__file__])