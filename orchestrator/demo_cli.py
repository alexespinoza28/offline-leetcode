#!/usr/bin/env python3
"""
Demonstration script for the Interview Coding Platform CLI interface.

This script shows all the CLI capabilities including:
- Command-line argument parsing
- JSON input/output handling
- All supported commands (run, explain, gen-tests, switch-lang)
- Error handling and validation
"""

import json
import tempfile
from pathlib import Path
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from cli import OrchestatorCLI


def demo_cli_capabilities():
    """Demonstrate all CLI capabilities."""
    print("🚀 Interview Coding Platform CLI Demo")
    print("=" * 50)
    
    cli = OrchestatorCLI()
    
    # Demo 1: Basic run command
    print("\n📋 Demo 1: Basic Run Command")
    print("-" * 30)
    result = cli.run([
        'run', 
        '--problem', 'two-sum', 
        '--lang', 'python', 
        '--code', 'def two_sum(nums, target): return [0, 1]'
    ])
    print(f"Exit code: {result}")
    
    # Demo 2: JSON output
    print("\n📋 Demo 2: JSON Output Format")
    print("-" * 30)
    result = cli.run([
        '--json-output',
        'run', 
        '--problem', 'add-two-numbers', 
        '--lang', 'cpp', 
        '--code', 'int main() { return 0; }'
    ])
    print(f"Exit code: {result}")
    
    # Demo 3: Explain command
    print("\n📋 Demo 3: Explain Command")
    print("-" * 30)
    result = cli.run([
        'explain',
        '--problem', 'binary-search',
        '--lang', 'java',
        '--code', 'public class Solution { public int search() { return -1; } }'
    ])
    print(f"Exit code: {result}")
    
    # Demo 4: Generate tests command
    print("\n📋 Demo 4: Generate Tests Command")
    print("-" * 30)
    result = cli.run([
        'gen-tests',
        '--problem', 'merge-intervals',
        '--count', '8',
        '--type', 'edge'
    ])
    print(f"Exit code: {result}")
    
    # Demo 5: Switch language command
    print("\n📋 Demo 5: Switch Language Command")
    print("-" * 30)
    result = cli.run([
        'switch-lang',
        '--problem', 'longest-substring',
        '--from-lang', 'python',
        '--to-lang', 'javascript'
    ])
    print(f"Exit code: {result}")
    
    # Demo 6: JSON input
    print("\n📋 Demo 6: JSON Input")
    print("-" * 30)
    json_input = {
        "command": "run",
        "problem": "valid-parentheses",
        "lang": "python",
        "code": "def isValid(s): return True",
        "tests": "sample"
    }
    result = cli.run([
        '--json-input', json.dumps(json_input),
        '--json-output'
    ])
    print(f"Exit code: {result}")
    
    # Demo 7: Code from file
    print("\n📋 Demo 7: Code from File")
    print("-" * 30)
    
    # Create a temporary code file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    print(fibonacci(10))

if __name__ == "__main__":
    main()
""")
        temp_file = f.name
    
    try:
        result = cli.run([
            'run',
            '--problem', 'fibonacci-number',
            '--lang', 'python',
            '--code-file', temp_file
        ])
        print(f"Exit code: {result}")
    finally:
        Path(temp_file).unlink()
    
    # Demo 8: Error handling
    print("\n📋 Demo 8: Error Handling")
    print("-" * 30)
    result = cli.run([
        'run',
        '--problem', 'test-problem',
        '--lang', 'python'
        # Missing --code parameter
    ])
    print(f"Exit code: {result}")
    
    # Demo 9: Invalid JSON input
    print("\n📋 Demo 9: Invalid JSON Handling")
    print("-" * 30)
    result = cli.run([
        '--json-input', '{"invalid": json syntax}',
        '--json-output'
    ])
    print(f"Exit code: {result}")
    
    print("\n✅ CLI Demo Complete!")
    print("=" * 50)


def demo_json_communication():
    """Demonstrate JSON communication patterns for VS Code extension."""
    print("\n🔗 JSON Communication Patterns for VS Code Extension")
    print("=" * 60)
    
    cli = OrchestatorCLI()
    
    # Example 1: Run command via JSON
    print("\n📤 Example 1: Run Command Request")
    request = {
        "command": "run",
        "problem": "two-sum",
        "lang": "python",
        "code": """
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
""",
        "tests": "all"
    }
    
    print("Request JSON:")
    print(json.dumps(request, indent=2))
    
    print("\n📥 Response:")
    result = cli.run([
        '--json-input', json.dumps(request),
        '--json-output'
    ])
    
    # Example 2: Explain command via JSON
    print("\n📤 Example 2: Explain Command Request")
    request = {
        "command": "explain",
        "problem": "binary-search",
        "lang": "cpp",
        "code": """
int binarySearch(vector<int>& nums, int target) {
    int left = 0, right = nums.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        else if (nums[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}
"""
    }
    
    print("Request JSON:")
    print(json.dumps(request, indent=2))
    
    print("\n📥 Response:")
    result = cli.run([
        '--json-input', json.dumps(request),
        '--json-output'
    ])
    
    # Example 3: Generate tests command via JSON
    print("\n📤 Example 3: Generate Tests Request")
    request = {
        "command": "gen-tests",
        "problem": "merge-sorted-arrays",
        "count": 12,
        "type": "stress"
    }
    
    print("Request JSON:")
    print(json.dumps(request, indent=2))
    
    print("\n📥 Response:")
    result = cli.run([
        '--json-input', json.dumps(request),
        '--json-output'
    ])
    
    print("\n✅ JSON Communication Demo Complete!")


if __name__ == "__main__":
    demo_cli_capabilities()
    demo_json_communication()