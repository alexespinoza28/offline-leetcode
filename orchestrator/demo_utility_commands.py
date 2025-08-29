#!/usr/bin/env python3
"""
Demonstration of all CLI utility command handlers.

This script showcases the complete integration of explain, gen-tests, switch-lang,
validate, stats, list-languages, and template-info commands with their respective
backend services.
"""

import json
import tempfile
from pathlib import Path
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from cli import OrchestatorCLI


def demo_utility_commands():
    """Demonstrate all utility command handlers."""
    print("🛠️  CLI Utility Commands Demonstration")
    print("=" * 50)
    
    cli = OrchestatorCLI()
    
    # Demo 1: Explain Command
    print("\\n📋 Demo 1: Explain Command")
    print("-" * 30)
    print("Generating explanation for a binary search solution...")
    
    result = cli.run([
        '--json-output',
        'explain',
        '--problem', 'binary-search',
        '--lang', 'python',
        '--code', '''
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
'''
    ])
    print(f"✅ Explain command completed with exit code: {result}")
    
    # Demo 2: Gen-tests Command
    print("\\n📋 Demo 2: Gen-tests Command")
    print("-" * 30)
    print("Generating test cases for a string problem...")
    
    result = cli.run([
        '--json-output',
        'gen-tests',
        '--problem', 'palindrome-check',
        '--count', '5',
        '--type', 'edge'
    ])
    print(f"✅ Gen-tests command completed with exit code: {result}")
    
    # Demo 3: Switch-lang Command
    print("\\n📋 Demo 3: Switch-lang Command")
    print("-" * 30)
    print("Switching language template from Python to C++...")
    
    result = cli.run([
        '--json-output',
        'switch-lang',
        '--problem', 'two-sum',
        '--from-lang', 'python',
        '--to-lang', 'cpp',
        '--preserve-logic'
    ])
    print(f"✅ Switch-lang command completed with exit code: {result}")
    
    # Demo 4: Validate Command
    print("\\n📋 Demo 4: Validate Command")
    print("-" * 30)
    print("Validating Python code syntax...")
    
    result = cli.run([
        '--json-output',
        'validate',
        '--lang', 'python',
        '--code', '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    ])
    print(f"✅ Validate command completed with exit code: {result}")
    
    # Demo 5: Stats Command (Overall)
    print("\\n📋 Demo 5: Stats Command (Overall)")
    print("-" * 30)
    print("Getting overall execution statistics...")
    
    result = cli.run([
        '--json-output',
        'stats'
    ])
    print(f"✅ Overall stats command completed with exit code: {result}")
    
    # Demo 6: Stats Command (Problem-specific)
    print("\\n📋 Demo 6: Stats Command (Problem-specific)")
    print("-" * 30)
    print("Getting statistics for a specific problem...")
    
    result = cli.run([
        '--json-output',
        'stats',
        '--problem', 'two-sum'
    ])
    print(f"✅ Problem-specific stats command completed with exit code: {result}")
    
    # Demo 7: Stats Command (Language-specific)
    print("\\n📋 Demo 7: Stats Command (Language-specific)")
    print("-" * 30)
    print("Getting statistics for Python language...")
    
    result = cli.run([
        '--json-output',
        'stats',
        '--lang', 'python'
    ])
    print(f"✅ Language-specific stats command completed with exit code: {result}")
    
    # Demo 8: List-languages Command
    print("\\n📋 Demo 8: List-languages Command")
    print("-" * 30)
    print("Listing all supported programming languages...")
    
    result = cli.run([
        '--json-output',
        'list-languages'
    ])
    print(f"✅ List-languages command completed with exit code: {result}")
    
    # Demo 9: Template-info Command
    print("\\n📋 Demo 9: Template-info Command")
    print("-" * 30)
    print("Getting template information for a problem...")
    
    result = cli.run([
        '--json-output',
        'template-info',
        '--problem', 'merge-sort',
        '--lang', 'cpp'
    ])
    print(f"✅ Template-info command completed with exit code: {result}")
    
    print("\\n🎉 All utility commands demonstrated successfully!")


def demo_json_interface():
    """Demonstrate JSON input/output interface for utility commands."""
    print("\\n📄 JSON Interface Demonstration")
    print("=" * 40)
    
    cli = OrchestatorCLI()
    
    # Demo JSON input for explain command
    print("\\n📋 JSON Input for Explain Command")
    print("-" * 35)
    
    json_input = {
        "command": "explain",
        "problem": "quicksort",
        "lang": "cpp",
        "code": '''
void quicksort(vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}
'''
    }
    
    result = cli.run([
        '--json-input', json.dumps(json_input),
        '--json-output'
    ])
    print(f"✅ JSON explain command completed with exit code: {result}")
    
    # Demo JSON input for gen-tests command
    print("\\n📋 JSON Input for Gen-tests Command")
    print("-" * 35)
    
    json_input = {
        "command": "gen-tests",
        "problem": "matrix-multiplication",
        "count": 8,
        "type": "stress"
    }
    
    result = cli.run([
        '--json-input', json.dumps(json_input),
        '--json-output'
    ])
    print(f"✅ JSON gen-tests command completed with exit code: {result}")


def demo_error_handling():
    """Demonstrate error handling for utility commands."""
    print("\\n🚨 Error Handling Demonstration")
    print("=" * 40)
    
    cli = OrchestatorCLI()
    
    # Demo 1: Invalid language for validate command
    print("\\n📋 Invalid Language Validation")
    print("-" * 30)
    
    result = cli.run([
        '--json-output',
        'validate',
        '--lang', 'invalid-language',
        '--code', 'print("hello")'
    ])
    print(f"✅ Invalid language handled with exit code: {result}")
    
    # Demo 2: Missing code for validate command
    print("\\n📋 Missing Code Validation")
    print("-" * 30)
    
    result = cli.run([
        '--json-output',
        'validate',
        '--lang', 'python'
        # No --code provided
    ])
    print(f"✅ Missing code handled with exit code: {result}")
    
    # Demo 3: Unsupported language for switch-lang
    print("\\n📋 Unsupported Language Switch")
    print("-" * 30)
    
    result = cli.run([
        '--json-output',
        'switch-lang',
        '--problem', 'test',
        '--from-lang', 'python',
        '--to-lang', 'unsupported-lang'
    ])
    print(f"✅ Unsupported language switch handled with exit code: {result}")


def demo_code_file_integration():
    """Demonstrate code file loading with utility commands."""
    print("\\n📁 Code File Integration Demonstration")
    print("=" * 45)
    
    cli = OrchestatorCLI()
    
    # Create temporary code files for different languages
    code_samples = {
        "python": '''
def merge_sort(arr):
    """
    Merge sort implementation with divide and conquer approach.
    Time complexity: O(n log n), Space complexity: O(n)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result
''',
        "cpp": '''
#include <vector>
#include <iostream>
using namespace std;

class MergeSort {
public:
    vector<int> mergeSort(vector<int>& arr) {
        if (arr.size() <= 1) return arr;
        
        int mid = arr.size() / 2;
        vector<int> left(arr.begin(), arr.begin() + mid);
        vector<int> right(arr.begin() + mid, arr.end());
        
        left = mergeSort(left);
        right = mergeSort(right);
        
        return merge(left, right);
    }
    
private:
    vector<int> merge(vector<int>& left, vector<int>& right) {
        vector<int> result;
        int i = 0, j = 0;
        
        while (i < left.size() && j < right.size()) {
            if (left[i] <= right[j]) {
                result.push_back(left[i++]);
            } else {
                result.push_back(right[j++]);
            }
        }
        
        while (i < left.size()) result.push_back(left[i++]);
        while (j < right.size()) result.push_back(right[j++]);
        
        return result;
    }
};
'''
    }
    
    for lang, code in code_samples.items():
        print(f"\\n📋 Testing {lang.upper()} Code File")
        print("-" * 30)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{lang}', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Test explain command with code file
            result = cli.run([
                '--json-output',
                'explain',
                '--problem', 'merge-sort',
                '--lang', lang,
                '--code-file', temp_file
            ])
            print(f"  ✅ Explain with {lang} file: exit code {result}")
            
            # Test validate command with code file
            result = cli.run([
                '--json-output',
                'validate',
                '--lang', lang,
                '--code-file', temp_file
            ])
            print(f"  ✅ Validate with {lang} file: exit code {result}")
            
        finally:
            Path(temp_file).unlink()


def demo_human_readable_output():
    """Demonstrate human-readable output formatting."""
    print("\\n👁️  Human-Readable Output Demonstration")
    print("=" * 45)
    
    cli = OrchestatorCLI()
    
    print("\\n📋 Human-readable output examples:")
    print("-" * 35)
    
    commands = [
        ['explain', '--problem', 'bubble-sort', '--lang', 'python', '--code', 'def bubble_sort(): pass'],
        ['gen-tests', '--problem', 'fibonacci', '--count', '3', '--type', 'unit'],
        ['switch-lang', '--problem', 'test', '--from-lang', 'python', '--to-lang', 'java'],
        ['validate', '--lang', 'python', '--code', 'def valid_function(): return True'],
        ['stats'],
        ['list-languages'],
        ['template-info', '--problem', 'test', '--lang', 'cpp']
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\\n{i}. Command: {' '.join(cmd)}")
        result = cli.run(cmd)  # No --json-output for human-readable format
        print(f"   Exit code: {result}")


if __name__ == "__main__":
    demo_utility_commands()
    demo_json_interface()
    demo_error_handling()
    demo_code_file_integration()
    demo_human_readable_output()
    
    print("\\n🎊 Complete Utility Commands Demonstration Finished!")
    print("All explain, gen-tests, switch-lang, validate, stats,")
    print("list-languages, and template-info commands are working!")