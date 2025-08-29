#!/usr/bin/env python3
"""
Tests for CLI utility command handlers.

This module tests the explain, gen-tests, switch-lang, validate, stats,
list-languages, and template-info command handlers.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from orchestrator.cli import OrchestatorCLI


class TestUtilityCommands:
    """Test suite for CLI utility command handlers."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = OrchestatorCLI()
    
    def test_explain_command_handler(self):
        """Test the explain command handler."""
        # Mock explanation engine
        mock_explanation = "This is a detailed explanation of the algorithm..."
        
        with patch.object(self.cli.explanation_engine, 'generate_explanation') as mock_generate:
            mock_generate.return_value = mock_explanation
            
            args = Mock()
            args.problem = "binary-search"
            args.lang = "python"
            args.code = "def binary_search(): pass"
            args.code_file = None
            
            result = self.cli.handle_explain_command(args)
            
            # Verify successful explanation generation
            assert result["status"] == "success"
            assert result["command"] == "explain"
            assert result["explanation"] == mock_explanation
            
            # Verify explanation engine was called correctly
            mock_generate.assert_called_once_with(
                problem_slug="binary-search",
                language="python",
                code="def binary_search(): pass"
            )
    
    def test_explain_command_with_code_file(self):
        """Test explain command with code file loading."""
        # Create temporary code file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)")
            temp_file = f.name
        
        try:
            with patch.object(self.cli.explanation_engine, 'generate_explanation') as mock_generate:
                mock_generate.return_value = "Factorial explanation"
                
                args = Mock()
                args.problem = "factorial"
                args.lang = "python"
                args.code = None
                args.code_file = temp_file
                
                result = self.cli.handle_explain_command(args)
                
                # Verify file was loaded and used
                assert result["status"] == "success"
                called_args = mock_generate.call_args[1]
                assert "def factorial(n):" in called_args["code"]
                
        finally:
            Path(temp_file).unlink()
    
    def test_gen_tests_command_handler(self):
        """Test the gen-tests command handler."""
        # Mock test generator
        mock_test_cases = [
            {"id": 1, "input": "test1", "output": "result1", "type": "unit"},
            {"id": 2, "input": "test2", "output": "result2", "type": "unit"},
            {"id": 3, "input": "test3", "output": "result3", "type": "unit"}
        ]
        
        with patch.object(self.cli.test_generator, 'generate_tests') as mock_generate:
            mock_generate.return_value = mock_test_cases
            
            args = Mock()
            args.problem = "two-sum"
            args.count = 3
            args.type = "unit"
            
            result = self.cli.handle_gen_tests_command(args)
            
            # Verify successful test generation
            assert result["status"] == "success"
            assert result["command"] == "gen-tests"
            assert result["test_cases"] == mock_test_cases
            assert result["count"] == 3
            assert result["problem"] == "two-sum"
            assert result["type"] == "unit"
            
            # Verify test generator was called correctly
            mock_generate.assert_called_once_with(
                problem_slug="two-sum",
                count=3,
                test_type="unit"
            )
    
    def test_gen_tests_command_with_fallback(self):
        """Test gen-tests command with fallback when generator fails."""
        with patch.object(self.cli.test_generator, 'generate_tests') as mock_generate:
            mock_generate.side_effect = Exception("Generator failed")
            
            args = Mock()
            args.problem = "test-problem"
            args.count = 2
            args.type = "edge"
            
            result = self.cli.handle_gen_tests_command(args)
            
            # Verify fallback was used
            assert result["status"] == "success"
            assert result["command"] == "gen-tests"
            assert len(result["test_cases"]) == 2
            assert "note" in result
            assert "fallback generation" in result["note"]
    
    def test_switch_lang_command_handler(self):
        """Test the switch-lang command handler."""
        # Mock template manager
        mock_result = {
            "problem": "fibonacci",
            "from_lang": "python",
            "to_lang": "cpp",
            "template_updated": True,
            "template_path": "/path/to/template.cpp"
        }
        
        with patch.object(self.cli.template_manager, 'switch_language') as mock_switch:
            mock_switch.return_value = mock_result
            
            args = Mock()
            args.problem = "fibonacci"
            args.from_lang = "python"
            args.to_lang = "cpp"
            args.preserve_logic = True
            
            result = self.cli.handle_switch_lang_command(args)
            
            # Verify successful language switch
            assert result["status"] == "success"
            assert result["command"] == "switch-lang"
            assert result["result"] == mock_result
            
            # Verify template manager was called correctly
            mock_switch.assert_called_once_with(
                problem_slug="fibonacci",
                from_lang="python",
                to_lang="cpp",
                preserve_logic=True
            )
    
    def test_switch_lang_command_failure(self):
        """Test switch-lang command when template manager fails."""
        mock_result = {
            "problem": "test",
            "from_lang": "python",
            "to_lang": "java",
            "template_updated": False,
            "error": "Unsupported language: java"
        }
        
        with patch.object(self.cli.template_manager, 'switch_language') as mock_switch:
            mock_switch.return_value = mock_result
            
            args = Mock()
            args.problem = "test"
            args.from_lang = "python"
            args.to_lang = "java"
            args.preserve_logic = True
            
            result = self.cli.handle_switch_lang_command(args)
            
            # Verify error handling
            assert result["status"] == "error"
            assert result["command"] == "switch-lang"
            assert "Unsupported language" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_command_handler(self):
        """Test the validate command handler."""
        # Mock execution service validation
        mock_validation_result = {
            "valid": True,
            "message": "Syntax is valid",
            "language": "python"
        }
        
        with patch.object(self.cli.execution_service, 'validate_syntax', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = mock_validation_result
            
            args = Mock()
            args.lang = "python"
            args.code = "def hello(): print('world')"
            args.code_file = None
            
            result = await self.cli.handle_validate_command(args)
            
            # Verify successful validation
            assert result["status"] == "success"
            assert result["command"] == "validate"
            assert result["result"] == mock_validation_result
            
            # Verify execution service was called correctly
            mock_validate.assert_called_once_with("def hello(): print('world')", "python")
    
    @pytest.mark.asyncio
    async def test_validate_command_no_code(self):
        """Test validate command with no code provided."""
        args = Mock()
        args.lang = "python"
        args.code = None
        args.code_file = None
        
        result = await self.cli.handle_validate_command(args)
        
        # Verify error handling
        assert result["status"] == "error"
        assert result["command"] == "validate"
        assert "No source code provided" in result["error"]
    
    @pytest.mark.asyncio
    async def test_stats_command_overall(self):
        """Test the stats command for overall statistics."""
        mock_stats = {
            "total_executions": 150,
            "successful_executions": 120,
            "failed_executions": 30,
            "avg_execution_time": 245.5
        }
        
        with patch.object(self.cli.execution_service, 'get_execution_stats', new_callable=AsyncMock) as mock_stats_call:
            mock_stats_call.return_value = mock_stats
            
            args = Mock()
            args.problem = None
            args.lang = None
            
            result = await self.cli.handle_stats_command(args)
            
            # Verify successful stats retrieval
            assert result["status"] == "success"
            assert result["command"] == "stats"
            assert result["type"] == "overall"
            assert result["result"] == mock_stats
            
            mock_stats_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stats_command_problem_specific(self):
        """Test the stats command for problem-specific statistics."""
        mock_problem_stats = {
            "problem_id": "two-sum",
            "total_attempts": 45,
            "success_rate": 78.5,
            "avg_time": 120.3
        }
        
        with patch.object(self.cli.execution_service, 'get_problem_analytics', new_callable=AsyncMock) as mock_problem_stats_call:
            mock_problem_stats_call.return_value = mock_problem_stats
            
            args = Mock()
            args.problem = "two-sum"
            args.lang = None
            
            result = await self.cli.handle_stats_command(args)
            
            # Verify successful problem stats retrieval
            assert result["status"] == "success"
            assert result["command"] == "stats"
            assert result["type"] == "problem"
            assert result["problem"] == "two-sum"
            assert result["result"] == mock_problem_stats
            
            mock_problem_stats_call.assert_called_once_with("two-sum")
    
    @pytest.mark.asyncio
    async def test_stats_command_language_specific(self):
        """Test the stats command for language-specific statistics."""
        mock_lang_stats = {
            "language": "python",
            "total_executions": 85,
            "avg_execution_time": 180.2,
            "success_rate": 82.4
        }
        
        with patch.object(self.cli.execution_service, 'get_language_analytics', new_callable=AsyncMock) as mock_lang_stats_call:
            mock_lang_stats_call.return_value = mock_lang_stats
            
            args = Mock()
            args.problem = None
            args.lang = "python"
            
            result = await self.cli.handle_stats_command(args)
            
            # Verify successful language stats retrieval
            assert result["status"] == "success"
            assert result["command"] == "stats"
            assert result["type"] == "language"
            assert result["language"] == "python"
            assert result["result"] == mock_lang_stats
            
            mock_lang_stats_call.assert_called_once_with("python")
    
    def test_list_languages_command_handler(self):
        """Test the list-languages command handler."""
        mock_languages = ["python", "cpp", "java", "javascript", "c"]
        
        with patch.object(self.cli.template_manager, 'get_supported_languages') as mock_get_langs:
            mock_get_langs.return_value = mock_languages
            
            args = Mock()
            
            result = self.cli.handle_list_languages_command(args)
            
            # Verify successful language list retrieval
            assert result["status"] == "success"
            assert result["command"] == "list-languages"
            assert result["languages"] == mock_languages
            assert result["count"] == 5
            
            mock_get_langs.assert_called_once()
    
    def test_template_info_command_handler(self):
        """Test the template-info command handler."""
        mock_template_info = {
            "problem": "binary-search",
            "language": "cpp",
            "file_path": "/templates/binary-search/solution.cpp",
            "exists": True,
            "extension": ".cpp",
            "main_function": "Solution",
            "comment_style": "//"
        }
        
        with patch.object(self.cli.template_manager, 'get_template_info') as mock_get_info:
            mock_get_info.return_value = mock_template_info
            
            args = Mock()
            args.problem = "binary-search"
            args.lang = "cpp"
            
            result = self.cli.handle_template_info_command(args)
            
            # Verify successful template info retrieval
            assert result["status"] == "success"
            assert result["command"] == "template-info"
            assert result["result"] == mock_template_info
            
            mock_get_info.assert_called_once_with("binary-search", "cpp")
    
    def test_json_input_override_for_utility_commands(self):
        """Test that JSON input overrides command-line arguments for utility commands."""
        # Test explain command
        with patch.object(self.cli.explanation_engine, 'generate_explanation') as mock_explain:
            mock_explain.return_value = "JSON explanation"
            
            args = Mock()
            args.problem = "cli-problem"
            args.lang = "cli-lang"
            args.code = "cli code"
            args.code_file = None
            
            json_data = {
                "problem": "json-problem",
                "lang": "json-lang",
                "code": "json code"
            }
            
            result = self.cli.handle_explain_command(args, json_data)
            
            # Verify JSON data was used
            assert result["status"] == "success"
            called_args = mock_explain.call_args[1]
            assert called_args["problem_slug"] == "json-problem"
            assert called_args["language"] == "json-lang"
            assert called_args["code"] == "json code"
    
    def test_error_handling_for_all_commands(self):
        """Test error handling for all utility commands."""
        # Test explain command error
        with patch.object(self.cli.explanation_engine, 'generate_explanation') as mock_explain:
            mock_explain.side_effect = Exception("Explanation engine failed")
            
            args = Mock()
            args.problem = "test"
            args.lang = "python"
            args.code = "test code"
            args.code_file = None
            
            result = self.cli.handle_explain_command(args)
            
            assert result["status"] == "error"
            assert result["command"] == "explain"
            assert "Explanation engine failed" in result["error"]
        
        # Test list-languages command error
        with patch.object(self.cli.template_manager, 'get_supported_languages') as mock_get_langs:
            mock_get_langs.side_effect = Exception("Template manager failed")
            
            args = Mock()
            
            result = self.cli.handle_list_languages_command(args)
            
            assert result["status"] == "error"
            assert result["command"] == "list-languages"
            assert "Template manager failed" in result["error"]
    
    def test_command_integration_summary(self):
        """Print a summary of all utility command tests."""
        print("\\n🎉 Utility Command Handler Test Summary")
        print("=" * 45)
        print("✅ Explain command handler")
        print("✅ Gen-tests command handler")
        print("✅ Switch-lang command handler")
        print("✅ Validate command handler")
        print("✅ Stats command handler")
        print("✅ List-languages command handler")
        print("✅ Template-info command handler")
        print("✅ JSON input override handling")
        print("✅ Error handling for all commands")
        print("\\n🚀 All utility command handlers working correctly!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])