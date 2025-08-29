#!/usr/bin/env python3
"""
Unit tests for the CLI interface framework.

Tests command parsing, JSON input/output handling, and command routing.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from orchestrator.cli import OrchestatorCLI, CLIError


class TestOrchestatorCLI:
    """Test cases for the OrchestatorCLI class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = OrchestatorCLI()
        # Mock the service dependencies
        self.cli.execution_service = Mock()
        self.cli.explanation_engine = Mock()
        self.cli.test_generator = Mock()
    
    def test_create_parser(self):
        """Test argument parser creation."""
        parser = self.cli.create_parser()
        
        # Test that parser is created
        assert parser is not None
        
        # Test global arguments
        args = parser.parse_args(["--json-output", "run", "--problem", "test", "--lang", "python", "--code", "print()"])
        assert args.json_output is True
        assert args.command == "run"
        assert args.problem == "test"
        assert args.lang == "python"
        assert args.code == "print()"
    
    def test_parse_json_input_valid(self):
        """Test parsing valid JSON input."""
        json_str = '{"command": "run", "problem": "two-sum", "lang": "python"}'
        result = self.cli.parse_json_input(json_str)
        
        assert result == {
            "command": "run",
            "problem": "two-sum",
            "lang": "python"
        }
    
    def test_parse_json_input_invalid(self):
        """Test parsing invalid JSON input."""
        with pytest.raises(CLIError, match="Invalid JSON input"):
            self.cli.parse_json_input('{"invalid": json}')
        
        with pytest.raises(CLIError, match="JSON input must be an object"):
            self.cli.parse_json_input('"not an object"')
    
    def test_load_code_from_file_success(self):
        """Test loading code from a file successfully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def solution():\n    return 42")
            temp_path = f.name
        
        try:
            code = self.cli.load_code_from_file(temp_path)
            assert code == "def solution():\n    return 42"
        finally:
            Path(temp_path).unlink()
    
    def test_load_code_from_file_not_found(self):
        """Test loading code from non-existent file."""
        with pytest.raises(CLIError, match="Code file not found"):
            self.cli.load_code_from_file("/nonexistent/file.py")
    
    @pytest.mark.asyncio
    async def test_handle_run_command_with_args(self):
        """Test handling run command with command-line arguments."""
        # Mock the execution service with async mock
        mock_result = {
            "status": "accepted",
            "overall_result": "OK",
            "passed_tests": 3,
            "total_tests": 3,
            "success_rate": 100.0,
            "total_time_ms": 150,
            "execution_id": "test-123",
            "message": "All tests passed!",
            "test_results": [
                {"test_id": "test_1", "status": "OK", "passed": True, "time_ms": 50, "memory_mb": 10},
                {"test_id": "test_2", "status": "OK", "passed": True, "time_ms": 45, "memory_mb": 9},
                {"test_id": "test_3", "status": "OK", "passed": True, "time_ms": 55, "memory_mb": 11}
            ]
        }
        
        with patch.object(self.cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            # Create mock args
            args = Mock()
            args.problem = "two-sum"
            args.lang = "python"
            args.code = "def solution(): return []"
            args.code_file = None
            args.tests = "all"
            
            result = await self.cli.handle_run_command(args)
            
            assert result["status"] == "success"
            assert result["command"] == "run"
            assert "result" in result
            
            cli_result = result["result"]
            assert cli_result["status"] == "OK"
            assert cli_result["summary"]["passed"] == 3
            assert cli_result["summary"]["total"] == 3
            assert cli_result["summary"]["total_time"] == 150
            assert len(cli_result["cases"]) == 3
            
            # Verify service was called correctly
            mock_execute.assert_called_once_with(
                code="def solution(): return []",
                language="py",  # Mapped from "python"
                problem_id="two-sum",
                user_id=None,
                session_id=None
            )
    
    def test_handle_run_command_with_json(self):
        """Test handling run command with JSON input."""
        # Mock the execution service
        mock_result = {"status": "OK"}
        self.cli.execution_service.run_solution.return_value = mock_result
        
        # Create mock args
        args = Mock()
        args.problem = None
        args.lang = None
        args.code = None
        args.code_file = None
        args.tests = "all"
        
        json_data = {
            "problem": "add-two-numbers",
            "lang": "cpp",
            "code": "int main() { return 0; }",
            "tests": "sample"
        }
        
        result = self.cli.handle_run_command(args, json_data)
        
        assert result["status"] == "success"
        
        # Verify service was called with JSON data
        self.cli.execution_service.run_solution.assert_called_once_with(
            problem_slug="add-two-numbers",
            language="cpp",
            code="int main() { return 0; }",
            test_set="sample"
        )
    
    def test_handle_run_command_with_code_file(self):
        """Test handling run command with code file."""
        # Create temporary code file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def solution(): return 42")
            temp_path = f.name
        
        try:
            # Mock the execution service
            mock_result = {"status": "OK"}
            self.cli.execution_service.run_solution.return_value = mock_result
            
            # Create mock args
            args = Mock()
            args.problem = "test"
            args.lang = "python"
            args.code = None
            args.code_file = temp_path
            args.tests = "all"
            
            result = self.cli.handle_run_command(args)
            
            assert result["status"] == "success"
            
            # Verify service was called with file content
            self.cli.execution_service.run_solution.assert_called_once_with(
                problem_slug="test",
                language="python",
                code="def solution(): return 42",
                test_set="all"
            )
        finally:
            Path(temp_path).unlink()
    
    def test_handle_run_command_no_code(self):
        """Test handling run command without code."""
        args = Mock()
        args.problem = "test"
        args.lang = "python"
        args.code = None
        args.code_file = None
        args.tests = "all"
        
        with pytest.raises(CLIError, match="No source code provided"):
            self.cli.handle_run_command(args)
    
    def test_handle_run_command_execution_error(self):
        """Test handling run command with execution error."""
        # Mock execution service to raise an exception
        self.cli.execution_service.run_solution.side_effect = Exception("Execution failed")
        
        args = Mock()
        args.problem = "test"
        args.lang = "python"
        args.code = "print('hello')"
        args.code_file = None
        args.tests = "all"
        
        result = self.cli.handle_run_command(args)
        
        assert result["status"] == "error"
        assert result["command"] == "run"
        assert "Execution failed" in result["error"]
    
    def test_handle_explain_command(self):
        """Test handling explain command."""
        # Mock the explanation engine
        mock_explanation = "This solution uses a hash map to find pairs..."
        self.cli.explanation_engine.generate_explanation.return_value = mock_explanation
        
        args = Mock()
        args.problem = "two-sum"
        args.lang = "python"
        args.code = "def solution(): pass"
        args.code_file = None
        
        result = self.cli.handle_explain_command(args)
        
        assert result["status"] == "success"
        assert result["command"] == "explain"
        assert result["explanation"] == mock_explanation
        
        # Verify engine was called correctly
        self.cli.explanation_engine.generate_explanation.assert_called_once_with(
            problem_slug="two-sum",
            language="python",
            code="def solution(): pass"
        )
    
    def test_handle_gen_tests_command(self):
        """Test handling gen-tests command."""
        # Mock the test generator
        mock_test_cases = [
            {"input": "[2, 7, 11, 15]", "output": "[0, 1]"},
            {"input": "[3, 2, 4]", "output": "[1, 2]"}
        ]
        self.cli.test_generator.generate_tests.return_value = mock_test_cases
        
        args = Mock()
        args.problem = "two-sum"
        args.count = 5
        args.type = "unit"
        
        result = self.cli.handle_gen_tests_command(args)
        
        assert result["status"] == "success"
        assert result["command"] == "gen-tests"
        assert result["test_cases"] == mock_test_cases
        
        # Verify generator was called correctly
        self.cli.test_generator.generate_tests.assert_called_once_with(
            problem_slug="two-sum",
            count=5,
            test_type="unit"
        )
    
    def test_handle_switch_lang_command(self):
        """Test handling switch-lang command."""
        args = Mock()
        args.problem = "two-sum"
        args.from_lang = "python"
        args.to_lang = "cpp"
        
        result = self.cli.handle_switch_lang_command(args)
        
        assert result["status"] == "success"
        assert result["command"] == "switch-lang"
        assert result["result"]["problem"] == "two-sum"
        assert result["result"]["from_lang"] == "python"
        assert result["result"]["to_lang"] == "cpp"
        assert result["result"]["template_updated"] is True
    
    @patch('sys.argv', ['cli.py', 'run', '--problem', 'test', '--lang', 'python', '--code', 'print()'])
    def test_run_success(self):
        """Test successful CLI run."""
        # Mock the execution service
        mock_result = {"status": "OK"}
        self.cli.execution_service.run_solution.return_value = mock_result
        
        exit_code = self.cli.run(['run', '--problem', 'test', '--lang', 'python', '--code', 'print()'])
        
        assert exit_code == 0
    
    @patch('sys.argv', ['cli.py', 'run', '--problem', 'test', '--lang', 'python'])
    def test_run_cli_error(self):
        """Test CLI run with CLIError."""
        exit_code = self.cli.run(['run', '--problem', 'test', '--lang', 'python'])
        
        assert exit_code == 1
    
    def test_run_json_input(self):
        """Test CLI run with JSON input."""
        # Mock the execution service
        mock_result = {"status": "OK"}
        self.cli.execution_service.run_solution.return_value = mock_result
        
        json_input = json.dumps({
            "command": "run",
            "problem": "test",
            "lang": "python",
            "code": "print('hello')"
        })
        
        exit_code = self.cli.run(['--json-input', json_input, '--json-output'])
        
        assert exit_code == 0
    
    def test_run_json_output(self):
        """Test CLI run with JSON output."""
        # Mock the execution service
        mock_result = {"status": "OK"}
        self.cli.execution_service.run_solution.return_value = mock_result
        
        with patch('builtins.print') as mock_print:
            exit_code = self.cli.run([
                '--json-output', 'run', '--problem', 'test', '--lang', 'python', 
                '--code', 'print()'
            ])
            
            assert exit_code == 0
            # Verify JSON output was printed
            mock_print.assert_called()
            printed_output = mock_print.call_args[0][0]
            parsed_output = json.loads(printed_output)
            assert parsed_output["status"] == "success"
    
    def test_print_human_readable_run_success(self):
        """Test human-readable output for successful run."""
        result = {
            "status": "success",
            "command": "run",
            "result": {
                "status": "OK",
                "summary": {
                    "passed": 3,
                    "total": 3,
                    "total_time": 150
                }
            }
        }
        
        with patch('builtins.print') as mock_print:
            self.cli._print_human_readable(result)
            
            # Check that success message was printed
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("✅ Run completed successfully" in call for call in calls)
            assert any("Tests: 3/3 passed" in call for call in calls)
            assert any("Time: 150ms" in call for call in calls)
    
    def test_print_human_readable_error(self):
        """Test human-readable output for error."""
        result = {
            "status": "error",
            "error": "Something went wrong"
        }
        
        with patch('builtins.print') as mock_print:
            self.cli._print_human_readable(result)
            
            mock_print.assert_called_once_with("❌ Error: Something went wrong")
    
    def test_print_human_readable_explain(self):
        """Test human-readable output for explain command."""
        result = {
            "status": "success",
            "command": "explain",
            "explanation": "This is a detailed explanation of the algorithm that is quite long and should be truncated in the output."
        }
        
        with patch('builtins.print') as mock_print:
            self.cli._print_human_readable(result)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("✅ Explain completed successfully" in call for call in calls)
            # Check for the actual truncated explanation
            explanation_call = [call for call in calls if call.startswith("Explanation:")][0]
            assert "..." in explanation_call  # Just check that it's truncated
    
    def test_print_human_readable_gen_tests(self):
        """Test human-readable output for gen-tests command."""
        result = {
            "status": "success",
            "command": "gen-tests",
            "test_cases": [
                {"input": "test1", "output": "result1"},
                {"input": "test2", "output": "result2"}
            ]
        }
        
        with patch('builtins.print') as mock_print:
            self.cli._print_human_readable(result)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("✅ Gen-tests completed successfully" in call for call in calls)
            assert any("Generated 2 test cases" in call for call in calls)
    
    def test_print_human_readable_switch_lang(self):
        """Test human-readable output for switch-lang command."""
        result = {
            "status": "success",
            "command": "switch-lang",
            "result": {
                "problem": "two-sum",
                "from_lang": "python",
                "to_lang": "cpp",
                "template_updated": True
            }
        }
        
        with patch('builtins.print') as mock_print:
            self.cli._print_human_readable(result)
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("✅ Switch-lang completed successfully" in call for call in calls)
            assert any("Switched two-sum from python to cpp" in call for call in calls)


class TestCLIIntegration:
    """Integration tests for the CLI interface."""
    
    def test_main_function_import(self):
        """Test that main function can be imported."""
        from orchestrator.cli import main
        assert callable(main)
    
    def test_main_module_import(self):
        """Test that __main__ module can be imported."""
        import orchestrator.__main__
        # Just verify it imports without error


if __name__ == "__main__":
    pytest.main([__file__])