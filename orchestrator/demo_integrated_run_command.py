#!/usr/bin/env python3
"""
Demonstration of the fully integrated run command with real execution service.

This script showcases the complete integration between the CLI run command
and the execution service, including real code execution, test case handling,
and comprehensive result reporting.
"""

import json
import tempfile
from pathlib import Path
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from cli import OrchestatorCLI


def demo_integrated_run_command():
    """Demonstrate the fully integrated run command with real execution service."""
    print("🚀 Integrated Run Command with Real Execution Service Demo")
    print("=" * 65)
    
    cli = OrchestatorCLI()
    
    # Demo 1: Successful Python execution
    print("\n📋 Demo 1: Successful Python Code Execution")
    print("-" * 45)
    print("Running a correct two-sum solution...")
    
    result = cli.run([
        '--json-output',
        'run',
        '--problem', 'two-sum',
        '--lang', 'python',
        '--code', '''
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Test the function
if __name__ == "__main__":
    print(two_sum([2, 7, 11, 15], 9))
'''
    ])
    print(f"✅ Python execution completed with exit code: {result}")
    
    # Demo 2: C++ compilation and execution
    print("\n📋 Demo 2: C++ Code Compilation and Execution")
    print("-" * 45)
    print("Running a C++ hello world program...")
    
    result = cli.run([
        '--json-output',
        'run',
        '--problem', 'hello-world',
        '--lang', 'cpp',
        '--code', '''
#include <iostream>
#include <vector>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
'''
    ])
    print(f"✅ C++ execution completed with exit code: {result}")
    
    # Demo 3: Error handling - compilation error
    print("\n📋 Demo 3: Compilation Error Handling")
    print("-" * 45)
    print("Testing compilation error handling...")
    
    result = cli.run([
        '--json-output',
        'run',
        '--problem', 'syntax-error-test',
        '--lang', 'cpp',
        '--code', '''
#include <iostream>
int main() {
    std::cout << "Missing semicolon" << std::endl
    return 0;
}
'''
    ])
    print(f"✅ Compilation error handled with exit code: {result}")
    
    # Demo 4: JSON input/output integration
    print("\n📋 Demo 4: JSON Input/Output Integration")
    print("-" * 45)
    print("Testing JSON communication interface...")
    
    json_input = {
        "command": "run",
        "problem": "binary-search",
        "lang": "python",
        "code": '''
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Test the function
if __name__ == "__main__":
    print(binary_search([1, 2, 3, 4, 5], 3))
'''
    }
    
    result = cli.run([
        '--json-input', json.dumps(json_input),
        '--json-output'
    ])
    print(f"✅ JSON interface test completed with exit code: {result}")
    
    # Demo 5: Code file loading
    print("\n📋 Demo 5: Code File Loading Integration")
    print("-" * 45)
    print("Testing code loading from file...")
    
    # Create a temporary code file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''
def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    """Test the factorial function."""
    test_cases = [0, 1, 5, 10]
    for n in test_cases:
        result = factorial(n)
        print(f"factorial({n}) = {result}")

if __name__ == "__main__":
    main()
''')
        temp_file = f.name
    
    try:
        result = cli.run([
            '--json-output',
            'run',
            '--problem', 'factorial-calculation',
            '--lang', 'python',
            '--code-file', temp_file
        ])
        print(f"✅ Code file loading completed with exit code: {result}")
    finally:
        Path(temp_file).unlink()
    
    # Demo 6: Language mapping and validation
    print("\n📋 Demo 6: Language Mapping and Validation")
    print("-" * 45)
    print("Testing language mapping (cpp -> cpp, python -> py)...")
    
    result = cli.run([
        '--json-output',
        'run',
        '--problem', 'language-mapping-test',
        '--lang', 'c++',  # Should map to 'cpp'
        '--code', '''
#include <iostream>
#include <string>

int main() {
    std::string message = "Language mapping works!";
    std::cout << message << std::endl;
    return 0;
}
'''
    ])
    print(f"✅ Language mapping test completed with exit code: {result}")
    
    # Demo 7: Test set selection
    print("\n📋 Demo 7: Test Set Selection")
    print("-" * 45)
    print("Testing different test set selections...")
    
    for test_set in ['all', 'sample', 'unit']:
        print(f"Running with test set: {test_set}")
        result = cli.run([
            '--json-output',
            'run',
            '--problem', f'test-set-{test_set}',
            '--lang', 'python',
            '--tests', test_set,
            '--code', '''
def simple_add(a, b):
    """Simple addition function for testing."""
    return a + b

if __name__ == "__main__":
    print(simple_add(2, 3))
'''
        ])
        print(f"  ✅ Test set '{test_set}' completed with exit code: {result}")
    
    # Demo 8: Error recovery and resilience
    print("\n📋 Demo 8: Error Recovery and Resilience")
    print("-" * 45)
    print("Testing error recovery with various error conditions...")
    
    error_cases = [
        {
            "name": "Empty code",
            "code": "",
            "expected": "No source code provided"
        },
        {
            "name": "Invalid language",
            "code": "print('hello')",
            "lang": "invalid-lang",
            "expected": "Language handling"
        },
        {
            "name": "Runtime error",
            "code": "1/0  # Division by zero",
            "expected": "Runtime error handling"
        }
    ]
    
    for case in error_cases:
        print(f"Testing: {case['name']}")
        try:
            result = cli.run([
                '--json-output',
                'run',
                '--problem', 'error-test',
                '--lang', case.get('lang', 'python'),
                '--code', case['code']
            ])
            print(f"  ✅ {case['name']} handled gracefully with exit code: {result}")
        except Exception as e:
            print(f"  ✅ {case['name']} error caught: {str(e)[:50]}...")
    
    print("\n🎉 All integration demos completed successfully!")
    print("The run command is fully integrated with the execution service.")


def demo_execution_service_features():
    """Demonstrate specific execution service features."""
    print("\n🔧 Execution Service Features Demo")
    print("=" * 40)
    
    cli = OrchestatorCLI()
    
    # Test default test cases for common problems
    common_problems = ['two-sum', 'add-two-numbers', 'longest-substring', 'valid-parentheses']
    
    for problem in common_problems:
        print(f"\n📝 Testing default test cases for: {problem}")
        result = cli.run([
            '--json-output',
            'run',
            '--problem', problem,
            '--lang', 'python',
            '--code', f'''
# Placeholder solution for {problem}
def solution():
    return "placeholder"

if __name__ == "__main__":
    print(solution())
'''
        ])
        print(f"  ✅ {problem} test cases loaded, exit code: {result}")
    
    print("\n✨ Execution service features demonstration complete!")


if __name__ == "__main__":
    demo_integrated_run_command()
    demo_execution_service_features()