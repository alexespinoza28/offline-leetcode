#!/usr/bin/env python3
"""
Demonstration of the CLI run command handler with real execution service integration.

This script shows how the CLI integrates with the execution service to run code
and return structured results.
"""

import asyncio
import json
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from cli import OrchestatorCLI


async def demo_run_command_integration():
    """Demonstrate the run command handler integration."""
    print("🚀 CLI Run Command Handler Integration Demo")
    print("=" * 60)
    
    cli = OrchestatorCLI()
    
    # Mock the execution service to simulate real behavior
    mock_execution_results = [
        {
            "name": "Python Success",
            "result": {
                "status": "accepted",
                "overall_result": "OK",
                "passed_tests": 2,
                "total_tests": 2,
                "success_rate": 100.0,
                "total_time_ms": 120,
                "execution_id": "demo-py-success",
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
        },
        {
            "name": "C++ Compilation Error",
            "result": {
                "status": "error",
                "message": "Compilation failed. Please check your syntax.",
                "logs": {
                    "compile": "main.cpp:5:1: error: expected ';' before '}' token"
                }
            }
        },
        {
            "name": "Python Wrong Answer",
            "result": {
                "status": "wrong_answer",
                "overall_result": "WA",
                "passed_tests": 1,
                "total_tests": 3,
                "success_rate": 33.3,
                "total_time_ms": 180,
                "execution_id": "demo-py-wa",
                "message": "1/3 test cases passed. Check your logic.",
                "test_results": [
                    {
                        "test_id": "test_1",
                        "status": "OK",
                        "passed": True,
                        "time_ms": 50
                    },
                    {
                        "test_id": "test_2",
                        "status": "WA",
                        "passed": False,
                        "time_ms": 65,
                        "diff": "Expected: 120\\nActual: 0"
                    },
                    {
                        "test_id": "test_3",
                        "status": "WA",
                        "passed": False,
                        "time_ms": 65,
                        "diff": "Expected: 3628800\\nActual: 0"
                    }
                ]
            }
        },
        {
            "name": "Java Timeout",
            "result": {
                "status": "time_limit_exceeded",
                "overall_result": "TLE",
                "passed_tests": 0,
                "total_tests": 1,
                "success_rate": 0.0,
                "total_time_ms": 2000,
                "execution_id": "demo-java-tle",
                "message": "Time limit exceeded. Your solution is too slow.",
                "test_results": [
                    {
                        "test_id": "test_1",
                        "status": "TLE",
                        "passed": False,
                        "time_ms": 2000,
                        "error": "Time limit exceeded (2.0s)"
                    }
                ]
            }
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(mock_execution_results):
        print(f"\\n📋 Demo {i+1}: {scenario['name']}")
        print("-" * 40)
        
        with patch.object(cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = scenario["result"]
            
            # Create test arguments
            args = Mock()
            args.problem = "test-problem"
            args.lang = "python"
            args.code = "def solution(): return []"
            args.code_file = None
            args.tests = "all"
            
            # Execute the run command
            result = await cli.handle_run_command(args)
            
            # Display results
            print(f"CLI Status: {result['status']}")
            print(f"Command: {result['command']}")
            
            if result["status"] == "success":
                cli_result = result["result"]
                print(f"Execution Status: {cli_result['status']}")
                print(f"Tests Passed: {cli_result['summary']['passed']}/{cli_result['summary']['total']}")
                print(f"Total Time: {cli_result['summary']['total_time']}ms")
                print(f"Success Rate: {cli_result['summary'].get('success_rate', 0):.1f}%")
                
                if cli_result.get("cases"):
                    print(f"Test Cases: {len(cli_result['cases'])}")
                    for case in cli_result["cases"][:2]:  # Show first 2 cases
                        status_icon = "✅" if case["status"] == "PASS" else "❌"
                        print(f"  {status_icon} {case['test_id']}: {case['status']} ({case['time']}ms)")
                        if case.get("diff"):
                            print(f"    Diff: {case['diff']}")
            else:
                print(f"Error: {result['error']}")
            
            # Verify service integration
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            print(f"Service called with language: {call_args[1]['language']}")
            print(f"Service called with problem_id: {call_args[1]['problem_id']}")


async def demo_json_communication():
    """Demonstrate JSON input/output for VS Code extension integration."""
    print("\\n🔗 JSON Communication Demo")
    print("=" * 40)
    
    cli = OrchestatorCLI()
    
    # Mock successful execution
    mock_result = {
        "status": "accepted",
        "overall_result": "OK",
        "passed_tests": 1,
        "total_tests": 1,
        "success_rate": 100.0,
        "total_time_ms": 85,
        "execution_id": "json-demo",
        "message": "All tests passed!",
        "test_results": [
            {
                "test_id": "test_1",
                "status": "OK",
                "input": "hello world",
                "expected_output": "HELLO WORLD",
                "actual_output": "HELLO WORLD",
                "error": "",
                "time_ms": 85,
                "memory_mb": 8.5,
                "diff": None,
                "passed": True
            }
        ]
    }
    
    with patch.object(cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = mock_result
        
        # Test JSON input
        args = Mock()
        args.problem = None
        args.lang = None
        args.code = None
        args.code_file = None
        args.tests = "all"
        
        json_data = {
            "problem": "string-to-upper",
            "lang": "python",
            "code": "def toUpper(s): return s.upper()",
            "tests": "sample"
        }
        
        print("📤 JSON Input:")
        print(json.dumps(json_data, indent=2))
        
        result = await cli.handle_run_command(args, json_data)
        
        print("\\n📥 CLI Response:")
        print(json.dumps(result, indent=2))
        
        # Verify JSON data was used correctly
        call_args = mock_execute.call_args
        assert call_args[1]["problem_id"] == "string-to-upper"
        assert call_args[1]["language"] == "py"  # Mapped from "python"
        assert "toUpper" in call_args[1]["code"]
        
        print("\\n✅ JSON communication working correctly!")


async def demo_language_mapping():
    """Demonstrate language name mapping from CLI to execution service."""
    print("\\n🔤 Language Mapping Demo")
    print("=" * 30)
    
    cli = OrchestatorCLI()
    
    # Test language mappings
    language_tests = [
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
    
    for cli_lang, expected_exec_lang in language_tests:
        with patch.object(cli.execution_service, 'execute_solution', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_result
            
            args = Mock()
            args.problem = "test"
            args.lang = cli_lang
            args.code = "// test code"
            args.code_file = None
            args.tests = "all"
            
            await cli.handle_run_command(args)
            
            # Verify correct language mapping
            call_args = mock_execute.call_args
            actual_lang = call_args[1]["language"]
            
            status = "✅" if actual_lang == expected_exec_lang else "❌"
            print(f"{status} {cli_lang} -> {actual_lang} (expected: {expected_exec_lang})")


async def main():
    """Run all demonstrations."""
    await demo_run_command_integration()
    await demo_json_communication()
    await demo_language_mapping()
    
    print("\\n🎉 All CLI Run Command Integration Demos Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())