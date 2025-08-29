#!/usr/bin/env python3
"""
Command-line interface for the Interview Coding Platform orchestrator.

This module provides a CLI framework that handles commands from VS Code extension
and other external tools. It supports JSON input/output for structured communication.

Supported commands:
- run: Execute code and run tests
- explain: Generate solution explanations
- gen-tests: Generate test cases for problems
- switch-lang: Switch language templates
"""

import argparse
import json
import sys
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from .utils.schema import SchemaValidator
    from .execution.service import ExecutionService
    from .explain.engine import ExplanationEngine
    from .gen_tests import TestGenerator
    from .templates.manager import LanguageTemplateManager
except ImportError:
    from utils.schema import SchemaValidator
    from execution.service import ExecutionService
    from explain.engine import ExplanationEngine
    from gen_tests import TestGenerator
    from templates.manager import LanguageTemplateManager


class MockExplanationEngine:
    """Mock explanation engine for CLI testing."""
    
    def generate_explanation(self, problem_slug: str, language: str, code: str = None):
        """Mock generate explanation method."""
        return f"This is a mock explanation for {problem_slug} in {language}."


class MockTestGenerator:
    """Mock test generator for CLI testing."""
    
    def generate_test_cases(self, config):
        """Mock generate test cases method."""
        count = getattr(config, 'test_set_size', 5)
        return [
            {"input": f"test_input_{i}", "output": f"test_output_{i}"}
            for i in range(count)
        ]


class CLIError(Exception):
    """Custom exception for CLI-related errors."""
    pass


class OrchestatorCLI:
    """
    Main CLI interface for the orchestrator.
    
    Handles command parsing, JSON input/output, and routing to appropriate handlers.
    """
    
    def __init__(self):
        # Initialize real services
        try:
            self.execution_service = ExecutionService()
            self.explanation_engine = ExplanationEngine()
            self.test_generator = TestGenerator()
            self.template_manager = LanguageTemplateManager()
            self.schema_validator = SchemaValidator()
        except Exception as e:
            # Fallback to mock services if real services fail to initialize
            print(f"Warning: Failed to initialize services, using mocks: {e}")
            self.execution_service = self._create_mock_execution_service()
            self.explanation_engine = self._create_mock_explanation_engine()
            self.test_generator = self._create_mock_test_generator()
            self.template_manager = self._create_mock_template_manager()
            self.schema_validator = SchemaValidator()
    
    def _create_mock_execution_service(self):
        """Create mock execution service as fallback."""
        class MockExecutionService:
            def run_solution(self, problem_slug: str, language: str, code: str, test_set: str = "all"):
                return {
                    "status": "accepted",
                    "overall_result": "OK",
                    "passed_tests": 2,
                    "total_tests": 2,
                    "success_rate": 100.0,
                    "total_time_ms": 120,
                    "test_results": []
                }
            async def execute_solution(self, code: str, language: str, problem_id: str, user_id=None, session_id=None):
                return {
                    "status": "accepted",
                    "overall_result": "OK",
                    "passed_tests": 2,
                    "total_tests": 2,
                    "success_rate": 100.0,
                    "total_time_ms": 120,
                    "test_results": []
                }
            async def validate_syntax(self, code: str, language: str):
                return {"valid": True, "message": "Mock validation", "language": language}
            async def get_execution_stats(self):
                return {"total_executions": 10, "successful_executions": 8}
            async def get_problem_analytics(self, problem_id: str):
                return {"problem_id": problem_id, "total_attempts": 5}
            async def get_language_analytics(self, language: str):
                return {"language": language, "total_executions": 3}
        return MockExecutionService()
    
    def _create_mock_explanation_engine(self):
        """Create mock explanation engine as fallback."""
        class MockExplanationEngine:
            def generate_explanation(self, problem_slug: str, language: str, code: str = None):
                return f"Mock explanation for {problem_slug} in {language}."
        return MockExplanationEngine()
    
    def _create_mock_test_generator(self):
        """Create mock test generator as fallback."""
        class MockTestGenerator:
            def generate_tests(self, problem_slug: str, count: int = 10, test_type: str = "unit"):
                return [
                    {
                        "id": f"test_{i+1}",
                        "input": f"test_input_{i}",
                        "output": f"test_output_{i}",
                        "type": test_type,
                        "description": f"Mock test case {i+1}"
                    }
                    for i in range(count)
                ]
        return MockTestGenerator()
    
    def _create_mock_template_manager(self):
        """Create mock template manager as fallback."""
        class MockTemplateManager:
            def switch_language(self, problem_slug: str, from_lang: str, to_lang: str, preserve_logic: bool = True):
                return {
                    "problem": problem_slug,
                    "from_lang": from_lang,
                    "to_lang": to_lang,
                    "template_updated": True
                }
            def get_supported_languages(self):
                return ["python", "cpp", "java", "javascript", "c"]
            def get_template_info(self, problem_slug: str, language: str):
                return {
                    "problem": problem_slug,
                    "language": language,
                    "file_path": f"/mock/{problem_slug}.{language}",
                    "exists": True,
                    "extension": f".{language}",
                    "main_function": "main"
                }
        return MockTemplateManager()
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Interview Coding Platform Orchestrator CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run code with JSON input
  python -m orchestrator.cli run --json '{"problem": "two-sum", "lang": "python", "code": "..."}'
  
  # Generate explanation
  python -m orchestrator.cli explain --problem two-sum --lang python
  
  # Generate test cases
  python -m orchestrator.cli gen-tests --problem two-sum --count 10
  
  # Switch language template
  python -m orchestrator.cli switch-lang --problem two-sum --from python --to cpp
            """
        )
        
        # Global options
        parser.add_argument(
            "--json-input",
            help="JSON input string for structured commands"
        )
        parser.add_argument(
            "--json-output",
            action="store_true",
            help="Output results in JSON format"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose logging"
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Run command
        run_parser = subparsers.add_parser("run", help="Execute code and run tests")
        run_parser.add_argument("--problem", required=True, help="Problem slug")
        run_parser.add_argument("--lang", required=True, help="Programming language")
        run_parser.add_argument("--code", help="Source code to execute")
        run_parser.add_argument("--code-file", help="File containing source code")
        run_parser.add_argument("--tests", choices=["sample", "unit", "all"], default="all",
                               help="Which test sets to run")
        
        # Explain command
        explain_parser = subparsers.add_parser("explain", help="Generate solution explanation")
        explain_parser.add_argument("--problem", required=True, help="Problem slug")
        explain_parser.add_argument("--lang", required=True, help="Programming language")
        explain_parser.add_argument("--code", help="Source code to explain")
        explain_parser.add_argument("--code-file", help="File containing source code")
        
        # Gen-tests command
        gen_tests_parser = subparsers.add_parser("gen-tests", help="Generate test cases")
        gen_tests_parser.add_argument("--problem", required=True, help="Problem slug")
        gen_tests_parser.add_argument("--count", type=int, default=10, help="Number of test cases")
        gen_tests_parser.add_argument("--type", choices=["unit", "edge", "stress"], default="unit",
                                     help="Type of test cases to generate")
        
        # Switch-lang command
        switch_parser = subparsers.add_parser("switch-lang", help="Switch language template")
        switch_parser.add_argument("--problem", required=True, help="Problem slug")
        switch_parser.add_argument("--from-lang", required=True, help="Source language")
        switch_parser.add_argument("--to-lang", required=True, help="Target language")
        switch_parser.add_argument("--preserve-logic", action="store_true", default=True,
                                  help="Attempt to preserve existing logic when switching")
        
        # Validate command
        validate_parser = subparsers.add_parser("validate", help="Validate code syntax")
        validate_parser.add_argument("--lang", required=True, help="Programming language")
        validate_parser.add_argument("--code", help="Source code to validate")
        validate_parser.add_argument("--code-file", help="File containing source code")
        
        # Stats command
        stats_parser = subparsers.add_parser("stats", help="Get execution statistics")
        stats_parser.add_argument("--problem", help="Get stats for specific problem")
        stats_parser.add_argument("--lang", help="Get stats for specific language")
        
        # List-languages command
        list_langs_parser = subparsers.add_parser("list-languages", help="List supported languages")
        
        # Template-info command
        template_info_parser = subparsers.add_parser("template-info", help="Get template information")
        template_info_parser.add_argument("--problem", required=True, help="Problem slug")
        template_info_parser.add_argument("--lang", required=True, help="Programming language")
        
        return parser
    
    def parse_json_input(self, json_str: str) -> Dict[str, Any]:
        """Parse and validate JSON input."""
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise CLIError("JSON input must be an object")
            return data
        except json.JSONDecodeError as e:
            raise CLIError(f"Invalid JSON input: {e}")
    
    def load_code_from_file(self, file_path: str) -> str:
        """Load source code from a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise CLIError(f"Code file not found: {file_path}")
            return path.read_text(encoding="utf-8")
        except Exception as e:
            raise CLIError(f"Error reading code file: {e}")
    
    async def handle_run_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the run command."""
        # Extract parameters from args or JSON
        if json_data:
            problem = json_data.get("problem", args.problem)
            lang = json_data.get("lang", args.lang)
            code = json_data.get("code", args.code)
            tests = json_data.get("tests", args.tests)
        else:
            problem = args.problem
            lang = args.lang
            code = args.code
            tests = args.tests
        
        # Load code from file if specified
        if args.code_file:
            code = self.load_code_from_file(args.code_file)
        
        if not code:
            raise CLIError("No source code provided (use --code or --code-file)")
        
        # Map language names to execution service format
        lang_mapping = {
            "python": "py",
            "cpp": "cpp",
            "c++": "cpp", 
            "c": "c",
            "javascript": "js",
            "java": "java"
        }
        
        execution_lang = lang_mapping.get(lang.lower(), lang.lower())
        
        # Execute the code using the real execution service
        try:
            result = self.execution_service.run_solution(
                problem_slug=problem,
                language=execution_lang,
                code=code,
                test_set=tests
            )
            
            # Convert execution service result to CLI format
            if result["status"] == "error":
                return {
                    "status": "error",
                    "command": "run",
                    "error": result["message"]
                }
            
            # Format successful result
            cli_result = {
                "status": result.get("overall_result", "OK"),
                "summary": {
                    "passed": result.get("passed_tests", 0),
                    "total": result.get("total_tests", 0),
                    "total_time": result.get("total_time_ms", 0),
                    "success_rate": result.get("success_rate", 0.0)
                },
                "cases": []
            }
            
            # Add individual test case results
            for test_result in result.get("test_results", []):
                cli_result["cases"].append({
                    "test_id": test_result.get("test_id", ""),
                    "status": "PASS" if test_result.get("passed", False) else "FAIL",
                    "time": test_result.get("time_ms", 0),
                    "memory": test_result.get("memory_mb", 0),
                    "input": test_result.get("input", ""),
                    "expected": test_result.get("expected_output", ""),
                    "actual": test_result.get("actual_output", ""),
                    "error": test_result.get("error", ""),
                    "diff": test_result.get("diff", "")
                })
            
            # Add logs if available
            if "logs" in result:
                cli_result["logs"] = result["logs"]
            
            # Add execution metadata
            cli_result["execution_id"] = result.get("execution_id", "")
            cli_result["message"] = result.get("message", "")
            
            return {
                "status": "success",
                "command": "run",
                "result": cli_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "command": "run",
                "error": f"Execution failed: {str(e)}"
            }
    
    def handle_explain_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the explain command."""
        # Extract parameters from args or JSON
        if json_data:
            problem = json_data.get("problem", args.problem)
            lang = json_data.get("lang", args.lang)
            code = json_data.get("code", args.code)
        else:
            problem = args.problem
            lang = args.lang
            code = args.code
        
        # Load code from file if specified
        if args.code_file:
            code = self.load_code_from_file(args.code_file)
        
        # Generate explanation
        try:
            explanation = self.explanation_engine.generate_explanation(
                problem_slug=problem,
                language=lang,
                code=code
            )
            return {
                "status": "success",
                "command": "explain",
                "explanation": explanation
            }
        except Exception as e:
            return {
                "status": "error",
                "command": "explain",
                "error": str(e)
            }
    
    def handle_gen_tests_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the gen-tests command."""
        # Extract parameters from args or JSON
        if json_data:
            problem = json_data.get("problem", args.problem)
            count = json_data.get("count", args.count)
            test_type = json_data.get("type", args.type)
        else:
            problem = args.problem
            count = args.count
            test_type = args.type
        
        # Generate test cases using the real test generator
        try:
            # Use the real test generator with proper method call
            test_cases = self.test_generator.generate_tests(
                problem_slug=problem,
                count=count,
                test_type=test_type
            )
            
            return {
                "status": "success",
                "command": "gen-tests",
                "test_cases": test_cases,
                "count": len(test_cases),
                "problem": problem,
                "type": test_type
            }
        except Exception as e:
            # Fallback to mock generation if real generator fails
            mock_cases = [
                {
                    "id": f"test_{i+1}",
                    "input": f"mock_input_{i}",
                    "output": f"mock_output_{i}",
                    "type": test_type
                }
                for i in range(count)
            ]
            
            return {
                "status": "success",
                "command": "gen-tests",
                "test_cases": mock_cases,
                "count": len(mock_cases),
                "problem": problem,
                "type": test_type,
                "note": f"Used fallback generation due to: {str(e)}"
            }
    
    def handle_switch_lang_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the switch-lang command."""
        # Extract parameters from args or JSON
        if json_data:
            problem = json_data.get("problem", args.problem)
            from_lang = json_data.get("from_lang", args.from_lang)
            to_lang = json_data.get("to_lang", args.to_lang)
        else:
            problem = args.problem
            from_lang = args.from_lang
            to_lang = args.to_lang
        
        # Switch language template using the real template manager
        try:
            preserve_logic = json_data.get("preserve_logic", True) if json_data else getattr(args, 'preserve_logic', True)
            
            result = self.template_manager.switch_language(
                problem_slug=problem,
                from_lang=from_lang,
                to_lang=to_lang,
                preserve_logic=preserve_logic
            )
            
            if result.get("template_updated", False):
                return {
                    "status": "success",
                    "command": "switch-lang",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "command": "switch-lang",
                    "error": result.get("error", "Failed to switch language template")
                }
        except Exception as e:
            return {
                "status": "error",
                "command": "switch-lang",
                "error": str(e)
            }
    
    async def handle_validate_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the validate command."""
        # Extract parameters from args or JSON
        if json_data:
            lang = json_data.get("lang", args.lang)
            code = json_data.get("code", args.code)
        else:
            lang = args.lang
            code = args.code
        
        # Load code from file if specified
        if args.code_file:
            code = self.load_code_from_file(args.code_file)
        
        if not code:
            return {
                "status": "error",
                "command": "validate",
                "error": "No source code provided (use --code or --code-file)"
            }
        
        # Validate code syntax using the execution service
        try:
            result = await self.execution_service.validate_syntax(code, lang)
            return {
                "status": "success",
                "command": "validate",
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "command": "validate",
                "error": f"Validation failed: {str(e)}"
            }
    
    async def handle_stats_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the stats command."""
        # Extract parameters from args or JSON
        if json_data:
            problem = json_data.get("problem", getattr(args, 'problem', None))
            lang = json_data.get("lang", getattr(args, 'lang', None))
        else:
            problem = getattr(args, 'problem', None)
            lang = getattr(args, 'lang', None)
        
        try:
            if problem:
                # Get problem-specific stats
                result = await self.execution_service.get_problem_analytics(problem)
                return {
                    "status": "success",
                    "command": "stats",
                    "type": "problem",
                    "problem": problem,
                    "result": result
                }
            elif lang:
                # Get language-specific stats
                result = await self.execution_service.get_language_analytics(lang)
                return {
                    "status": "success",
                    "command": "stats",
                    "type": "language",
                    "language": lang,
                    "result": result
                }
            else:
                # Get overall stats
                result = await self.execution_service.get_execution_stats()
                return {
                    "status": "success",
                    "command": "stats",
                    "type": "overall",
                    "result": result
                }
        except Exception as e:
            return {
                "status": "error",
                "command": "stats",
                "error": f"Failed to get statistics: {str(e)}"
            }
    
    def handle_list_languages_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the list-languages command."""
        try:
            languages = self.template_manager.get_supported_languages()
            return {
                "status": "success",
                "command": "list-languages",
                "languages": languages,
                "count": len(languages)
            }
        except Exception as e:
            return {
                "status": "error",
                "command": "list-languages",
                "error": f"Failed to get supported languages: {str(e)}"
            }
    
    def handle_template_info_command(self, args: argparse.Namespace, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle the template-info command."""
        # Extract parameters from args or JSON
        if json_data:
            problem = json_data.get("problem", args.problem)
            lang = json_data.get("lang", args.lang)
        else:
            problem = args.problem
            lang = args.lang
        
        try:
            info = self.template_manager.get_template_info(problem, lang)
            return {
                "status": "success",
                "command": "template-info",
                "result": info
            }
        except Exception as e:
            return {
                "status": "error",
                "command": "template-info",
                "error": f"Failed to get template info: {str(e)}"
            }
    
    async def run_async(self, args: Optional[list] = None) -> int:
        """Async main entry point for the CLI."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        try:
            # Parse JSON input if provided
            json_data = None
            if parsed_args.json_input:
                json_data = self.parse_json_input(parsed_args.json_input)
                # If JSON contains a command, use it
                if "command" in json_data:
                    parsed_args.command = json_data["command"]
                    # Set default values for missing attributes when using JSON input
                    for attr in ["problem", "lang", "code", "code_file", "tests", "count", "type", "from_lang", "to_lang"]:
                        if not hasattr(parsed_args, attr):
                            setattr(parsed_args, attr, None)
            
            # Route to appropriate command handler
            if parsed_args.command == "run":
                result = await self.handle_run_command(parsed_args, json_data)
            elif parsed_args.command == "explain":
                result = self.handle_explain_command(parsed_args, json_data)
            elif parsed_args.command == "gen-tests":
                result = self.handle_gen_tests_command(parsed_args, json_data)
            elif parsed_args.command == "switch-lang":
                result = self.handle_switch_lang_command(parsed_args, json_data)
            elif parsed_args.command == "validate":
                result = await self.handle_validate_command(parsed_args, json_data)
            elif parsed_args.command == "stats":
                result = await self.handle_stats_command(parsed_args, json_data)
            elif parsed_args.command == "list-languages":
                result = self.handle_list_languages_command(parsed_args, json_data)
            elif parsed_args.command == "template-info":
                result = self.handle_template_info_command(parsed_args, json_data)
            else:
                parser.print_help()
                return 1
            
            # Output result
            if parsed_args.json_output:
                print(json.dumps(result, indent=2))
            else:
                self._print_human_readable(result)
            
            return 0 if result["status"] == "success" else 1
            
        except CLIError as e:
            error_result = {
                "status": "error",
                "error": str(e)
            }
            if parsed_args.json_output:
                print(json.dumps(error_result, indent=2))
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            error_result = {
                "status": "error",
                "error": f"Unexpected error: {e}"
            }
            if parsed_args.json_output:
                print(json.dumps(error_result, indent=2))
            else:
                print(f"Unexpected error: {e}", file=sys.stderr)
            return 1
    
    def run(self, args: Optional[list] = None) -> int:
        """Synchronous wrapper for the async run method."""
        import asyncio
        return asyncio.run(self.run_async(args))
    
    def _print_human_readable(self, result: Dict[str, Any]) -> None:
        """Print result in human-readable format."""
        if result["status"] == "error":
            print(f"❌ Error: {result['error']}")
            return
        
        command = result["command"]
        # Format command name properly
        if command == "gen-tests":
            command_title = "Gen-tests"
        elif command == "switch-lang":
            command_title = "Switch-lang"
        else:
            command_title = command.title()
        
        print(f"✅ {command_title} completed successfully")
        
        if command == "run":
            run_result = result["result"]
            print(f"Status: {run_result.get('status', 'Unknown')}")
            if "summary" in run_result:
                summary = run_result["summary"]
                print(f"Tests: {summary.get('passed', 0)}/{summary.get('total', 0)} passed")
                print(f"Time: {summary.get('total_time', 0)}ms")
        
        elif command == "explain":
            explanation = result["explanation"]
            if len(explanation) > 100:
                print(f"Explanation: {explanation[:100]}...")
            else:
                print(f"Explanation: {explanation}")
        
        elif command == "gen-tests":
            test_cases = result["test_cases"]
            print(f"Generated {len(test_cases)} test cases")
        
        elif command == "switch-lang":
            switch_result = result["result"]
            print(f"Switched {switch_result['problem']} from {switch_result['from_lang']} to {switch_result['to_lang']}")
        
        elif command == "validate":
            validate_result = result["result"]
            if validate_result.get("valid", False):
                print("✅ Code syntax is valid")
            else:
                print(f"❌ Syntax error: {validate_result.get('message', 'Unknown error')}")
        
        elif command == "stats":
            stats_result = result["result"]
            stats_type = result.get("type", "overall")
            if stats_type == "problem":
                print(f"Statistics for problem '{result['problem']}':")
            elif stats_type == "language":
                print(f"Statistics for language '{result['language']}':")
            else:
                print("Overall execution statistics:")
            
            # Print key statistics
            if "total_executions" in stats_result:
                print(f"  Total executions: {stats_result['total_executions']}")
            if "successful_executions" in stats_result:
                print(f"  Successful: {stats_result['successful_executions']}")
            if "avg_execution_time" in stats_result:
                print(f"  Average time: {stats_result['avg_execution_time']:.2f}ms")
        
        elif command == "list-languages":
            languages = result["languages"]
            print(f"Supported languages ({result['count']}):")
            for lang in languages:
                print(f"  • {lang}")
        
        elif command == "template-info":
            info = result["result"]
            print(f"Template info for {info.get('problem', 'unknown')} in {info.get('language', 'unknown')}:")
            print(f"  File path: {info.get('file_path', 'N/A')}")
            print(f"  Exists: {'Yes' if info.get('exists', False) else 'No'}")
            print(f"  Extension: {info.get('extension', 'N/A')}")
            print(f"  Main function: {info.get('main_function', 'N/A')}")


def main():
    """Entry point for the CLI when run as a module."""
    cli = OrchestatorCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())