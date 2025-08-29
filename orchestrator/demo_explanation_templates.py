#!/usr/bin/env python3
"""
Demo script showcasing the template-based explanation system.

This demonstrates the complete explanation generation workflow including:
- Template loading and pattern matching
- Code analysis and pattern detection
- Variable substitution and rendering
- Multi-language support
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from explain.engine import ExplanationEngine, CodeAnalyzer
from explain.template_loader import TemplateLoader

def demonstrate_template_loading():
    """Demonstrate template loading and pattern matching."""
    print("TEMPLATE LOADING AND PATTERN MATCHING")
    print("=" * 50)
    
    # Create temporary templates directory
    temp_dir = tempfile.mkdtemp()
    templates_dir = Path(temp_dir) / "templates"
    
    try:
        # Create explanation engine (will create default templates)
        engine = ExplanationEngine(str(templates_dir))
        
        print(f"Templates directory: {templates_dir}")
        print(f"Available templates: {engine.template_loader.list_templates()}")
        
        # Test template finding
        test_problems = [
            ("two-sum", ["array", "hash-table"]),
            ("reverse-string", ["string"]),
            ("binary-tree-inorder", ["tree", "traversal"]),
            ("fibonacci", ["dynamic-programming"]),
            ("unknown-problem", ["general"])
        ]
        
        print("\\nTemplate Selection Results:")
        print("-" * 30)
        
        for problem, tags in test_problems:
            template = engine.template_loader.find_template(problem, tags)
            print(f"Problem: {problem:20} → Template: {template}")
        
        return templates_dir
        
    except Exception as e:
        print(f"Error in template loading demo: {e}")
        shutil.rmtree(temp_dir)
        return None

def demonstrate_code_analysis():
    """Demonstrate code analysis capabilities."""
    print("\\n\\nCODE ANALYSIS DEMONSTRATION")
    print("=" * 50)
    
    analyzer = CodeAnalyzer()
    
    # Test different code examples
    code_examples = [
        {
            "name": "Two Sum (Hash Map)",
            "language": "python",
            "code": '''
def two_sum(nums, target):
    num_dict = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[num] = i
    return []
'''
        },
        {
            "name": "Two Pointers",
            "language": "python", 
            "code": '''
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return []
'''
        },
        {
            "name": "Dynamic Programming",
            "language": "python",
            "code": '''
def fibonacci(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
'''
        },
        {
            "name": "C++ STL Usage",
            "language": "cpp",
            "code": '''
#include <vector>
#include <unordered_map>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> numMap;
    for (int i = 0; i < nums.size(); i++) {
        int complement = target - nums[i];
        if (numMap.find(complement) != numMap.end()) {
            return {numMap[complement], i};
        }
        numMap[nums[i]] = i;
    }
    return {};
}
'''
        }
    ]
    
    for example in code_examples:
        print(f"\\nAnalyzing: {example['name']} ({example['language']})")
        print("-" * 40)
        
        analysis = analyzer.analyze_code(example['code'], example['language'])
        
        print(f"Language: {analysis['language']}")
        print(f"Algorithm Type: {analysis['algorithm_type']}")
        print(f"Time Complexity: {analysis['time_complexity']}")
        print(f"Space Complexity: {analysis['space_complexity']}")
        
        if analysis['data_structures']:
            print(f"Data Structures: {', '.join(analysis['data_structures'])}")
        
        if analysis['patterns']:
            print(f"Patterns: {', '.join(analysis['patterns'])}")

def demonstrate_explanation_generation(templates_dir):
    """Demonstrate complete explanation generation."""
    print("\\n\\nEXPLANATION GENERATION DEMONSTRATION")
    print("=" * 50)
    
    if not templates_dir:
        print("Skipping explanation generation - templates not available")
        return
    
    engine = ExplanationEngine(str(templates_dir))
    
    # Test cases with different problems and code
    test_cases = [
        {
            "problem": "two-sum",
            "language": "python",
            "tags": ["array", "hash-table"],
            "difficulty": "easy",
            "code": '''
def two_sum(nums, target):
    num_dict = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[num] = i
    return []
'''
        },
        {
            "problem": "reverse-string",
            "language": "python",
            "tags": ["string", "two-pointers"],
            "difficulty": "easy",
            "code": '''
def reverse_string(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
'''
        },
        {
            "problem": "fibonacci",
            "language": "python",
            "tags": ["dynamic-programming"],
            "difficulty": "easy",
            "code": '''
def fibonacci(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
'''
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n{i}. Generating explanation for: {test_case['problem']}")
        print("-" * 60)
        
        explanation = engine.generate_explanation(
            problem_slug=test_case['problem'],
            language=test_case['language'],
            code=test_case['code'],
            tags=test_case['tags'],
            difficulty=test_case['difficulty']
        )
        
        # Show first 500 characters of explanation
        preview = explanation[:500] + "..." if len(explanation) > 500 else explanation
        print(preview)
        print(f"\\n[Full explanation length: {len(explanation)} characters]")

def demonstrate_template_customization():
    """Demonstrate template customization and variable substitution."""
    print("\\n\\nTEMPLATE CUSTOMIZATION DEMONSTRATION")
    print("=" * 50)
    
    # Create temporary templates directory
    temp_dir = tempfile.mkdtemp()
    templates_dir = Path(temp_dir) / "custom_templates"
    templates_dir.mkdir(parents=True)
    
    try:
        # Create custom template
        custom_template = '''---
patterns: ["custom", "demo"]
difficulty: medium
tags: [algorithm, demo]
---

# Custom Solution Explanation for {{problem_slug}}

## Problem Analysis
This {{difficulty}} problem requires a {{algorithm_type}} approach using {{language}}.

## Algorithm Overview
The solution uses the following data structures: {{data_structures}}

## Complexity Analysis
- **Time Complexity**: {{time_complexity}}
- **Space Complexity**: {{space_complexity}}

## Key Patterns
{{patterns}}

## Language-Specific Notes
This solution is optimized for {{language}} and takes advantage of:
- Built-in data structures
- Language-specific optimizations
- Idiomatic coding patterns

## Conclusion
This approach provides an efficient solution with {{time_complexity}} time complexity.
'''
        
        # Write custom template
        template_file = templates_dir / "custom_demo.md"
        template_file.write_text(custom_template, encoding='utf-8')
        
        # Create template loader
        loader = TemplateLoader(str(templates_dir))
        
        # Test variable substitution
        variables = {
            "problem_slug": "custom-demo-problem",
            "difficulty": "medium",
            "algorithm_type": "iterative",
            "language": "Python",
            "data_structures": "dictionary, list",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "patterns": "Hash Map, Single Pass"
        }
        
        print("Custom Template Variables:")
        for key, value in variables.items():
            print(f"  {key}: {value}")
        
        print("\\nRendered Template:")
        print("-" * 30)
        
        rendered = loader.render_template("custom_demo", variables)
        print(rendered[:800] + "..." if len(rendered) > 800 else rendered)
        
    except Exception as e:
        print(f"Error in template customization demo: {e}")
    finally:
        shutil.rmtree(temp_dir)

def demonstrate_hints_system():
    """Demonstrate the hints generation system."""
    print("\\n\\nHINTS GENERATION DEMONSTRATION")
    print("=" * 50)
    
    engine = ExplanationEngine()
    
    test_problems = [
        ("two-sum", "easy"),
        ("three-sum", "medium"), 
        ("binary-tree-traversal", "medium"),
        ("longest-palindrome", "hard"),
        ("dynamic-programming-problem", "hard")
    ]
    
    for problem, difficulty in test_problems:
        print(f"\\nHints for: {problem} ({difficulty})")
        print("-" * 30)
        
        hints = engine.get_hints(problem, difficulty)
        
        for i, hint in enumerate(hints, 1):
            print(f"{i}. {hint}")

def main():
    """Main demonstration function."""
    print("TEMPLATE-BASED EXPLANATION SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases the comprehensive explanation generation system")
    print("with template-based rendering, code analysis, and pattern matching.\\n")
    
    try:
        # Run demonstrations
        templates_dir = demonstrate_template_loading()
        demonstrate_code_analysis()
        demonstrate_explanation_generation(templates_dir)
        demonstrate_template_customization()
        demonstrate_hints_system()
        
        print("\\n" + "=" * 60)
        print("✓ DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("The template-based explanation system provides:")
        print("• Pattern-based template selection")
        print("• Comprehensive code analysis")
        print("• Variable substitution in templates")
        print("• Multi-language support")
        print("• Customizable explanation templates")
        print("• Progressive hint generation")
        print("• Markdown template rendering")
        
        # Clean up
        if templates_dir:
            shutil.rmtree(templates_dir.parent)
        
    except Exception as e:
        print(f"\\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()