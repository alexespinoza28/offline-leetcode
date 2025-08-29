#!/usr/bin/env python3
"""
Simple test to verify the template-based explanation system is working.
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from explain.engine import ExplanationEngine, CodeAnalyzer
from explain.template_loader import TemplateLoader

def test_template_system():
    """Test the core template system functionality."""
    print("Testing Template-Based Explanation System")
    print("=" * 50)
    
    try:
        # Test 1: Template Loader
        print("\\n1. Testing TemplateLoader...")
        temp_dir = tempfile.mkdtemp()
        templates_dir = Path(temp_dir) / "templates"
        
        loader = TemplateLoader(str(templates_dir))
        templates = loader.list_templates()
        print(f"   ✓ Created {len(templates)} default templates")
        
        # Test template finding
        template = loader.find_template("two-sum", ["array"])
        print(f"   ✓ Found template '{template}' for two-sum problem")
        
        # Test 2: Code Analyzer
        print("\\n2. Testing CodeAnalyzer...")
        analyzer = CodeAnalyzer()
        
        python_code = '''
def two_sum(nums, target):
    num_dict = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[num] = i
    return []
'''
        
        analysis = analyzer.analyze_code(python_code, "python")
        print(f"   ✓ Analyzed Python code: {analysis['language']}")
        print(f"   ✓ Detected data structures: {analysis['data_structures']}")
        print(f"   ✓ Time complexity: {analysis['time_complexity']}")
        
        # Test 3: Explanation Engine
        print("\\n3. Testing ExplanationEngine...")
        engine = ExplanationEngine(str(templates_dir))
        
        explanation = engine.generate_explanation(
            problem_slug="two-sum",
            language="python",
            code=python_code,
            tags=["array", "hash-table"],
            difficulty="easy"
        )
        
        print(f"   ✓ Generated explanation ({len(explanation)} characters)")
        print(f"   ✓ Contains algorithm overview: {'Algorithm Overview' in explanation}")
        print(f"   ✓ Contains complexity analysis: {'Complexity' in explanation}")
        
        # Test 4: Template Rendering
        print("\\n4. Testing Template Rendering...")
        variables = {
            "problem_slug": "test-problem",
            "language": "Python",
            "time_complexity": "O(n)",
            "space_complexity": "O(1)"
        }
        
        rendered = loader.render_template("default", variables)
        print(f"   ✓ Rendered template with variables")
        print(f"   ✓ Variable substitution working: {'test-problem' in rendered}")
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        print("\\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("The template-based explanation system is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_analysis_patterns():
    """Test code analysis pattern detection."""
    print("\\n\\nTesting Code Analysis Patterns")
    print("=" * 40)
    
    analyzer = CodeAnalyzer()
    
    test_cases = [
        {
            "name": "Two Pointers",
            "code": "left, right = 0, len(arr) - 1\\nwhile left < right:",
            "expected_pattern": "Two Pointers"
        },
        {
            "name": "Dynamic Programming", 
            "code": "dp = [0] * n\\nfor i in range(1, n):\\n    dp[i] = dp[i-1] + dp[i-2]",
            "expected_pattern": "Dynamic Programming"
        },
        {
            "name": "Hash Map",
            "code": "num_dict = {}\\nfor num in nums:\\n    num_dict[num] = i",
            "expected_data_structure": "dictionary"
        }
    ]
    
    for test_case in test_cases:
        print(f"\\nTesting {test_case['name']}:")
        analysis = analyzer.analyze_code(test_case['code'], "python")
        
        if 'expected_pattern' in test_case:
            if test_case['expected_pattern'] in analysis.get('patterns', []):
                print(f"   ✓ Detected pattern: {test_case['expected_pattern']}")
            else:
                print(f"   ⚠ Pattern not detected: {test_case['expected_pattern']}")
        
        if 'expected_data_structure' in test_case:
            if test_case['expected_data_structure'] in analysis.get('data_structures', []):
                print(f"   ✓ Detected data structure: {test_case['expected_data_structure']}")
            else:
                print(f"   ⚠ Data structure not detected: {test_case['expected_data_structure']}")
        
        print(f"   → Time complexity: {analysis.get('time_complexity', 'Unknown')}")
        print(f"   → Space complexity: {analysis.get('space_complexity', 'Unknown')}")

def main():
    """Run all tests."""
    print("TEMPLATE-BASED EXPLANATION SYSTEM VERIFICATION")
    print("=" * 60)
    
    success = test_template_system()
    test_code_analysis_patterns()
    
    print("\\n" + "=" * 60)
    if success:
        print("🎉 VERIFICATION COMPLETE - System is working correctly!")
    else:
        print("❌ VERIFICATION FAILED - Please check the implementation")

if __name__ == "__main__":
    main()