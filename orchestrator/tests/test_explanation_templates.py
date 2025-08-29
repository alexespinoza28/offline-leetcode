#!/usr/bin/env python3
"""
Tests for the template-based explanation system.
"""

import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from explain.engine import ExplanationEngine, CodeAnalyzer
from explain.template_loader import TemplateLoader

class TestTemplateLoader:
    """Test cases for TemplateLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.temp_dir) / "templates"
        self.templates_dir.mkdir(parents=True)
        self.loader = TemplateLoader(str(self.templates_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_template(self, name: str, patterns: list, content: str):
        """Create a test template file."""
        template_file = self.templates_dir / f"{name}.md"
        
        front_matter = "---\\n"
        front_matter += f"patterns: {patterns}\\n"
        front_matter += "difficulty: medium\\n"
        front_matter += "tags: [algorithm]\\n"
        front_matter += "---\\n\\n"
        
        full_content = front_matter + content
        template_file.write_text(full_content, encoding='utf-8')
    
    def test_template_loading(self):
        """Test loading templates from files."""
        # Create test template
        self.create_test_template(
            "test_template",
            ["test", "example"],
            "This is a test template with {{variable}} substitution."
        )
        
        # Reload templates
        self.loader.reload_templates()
        
        # Check template was loaded
        templates = self.loader.list_templates()
        assert "test_template" in templates
        
        # Check metadata
        metadata = self.loader.get_template_metadata("test_template")
        assert metadata["patterns"] == ["test", "example"]
        assert metadata["difficulty"] == "medium"
    
    def test_template_finding(self):
        """Test finding best matching template."""
        # Create templates with different patterns
        self.create_test_template(
            "array_template",
            ["array", "two-sum"],
            "Array solution template"
        )
        
        self.create_test_template(
            "string_template", 
            ["string", "palindrome"],
            "String solution template"
        )
        
        # Reload templates
        self.loader.reload_templates()
        
        # Test pattern matching
        template = self.loader.find_template("two-sum-problem")
        assert template == "array_template"
        
        template = self.loader.find_template("palindrome-check")
        assert template == "string_template"
        
        # Test with tags
        template = self.loader.find_template("unknown-problem", tags=["array"])
        assert template == "array_template"
    
    def test_template_rendering(self):
        """Test template rendering with variable substitution."""
        # Create template with variables
        self.create_test_template(
            "variable_template",
            ["test"],
            "Problem: {{problem_slug}}\\nLanguage: {{language}}\\nComplexity: {{time_complexity}}"
        )
        
        # Reload templates
        self.loader.reload_templates()
        
        # Render template
        variables = {
            "problem_slug": "test-problem",
            "language": "python",
            "time_complexity": "O(n)"
        }
        
        result = self.loader.render_template("variable_template", variables)
        
        assert "Problem: test-problem" in result
        assert "Language: python" in result
        assert "Complexity: O(n)" in result
    
    def test_default_templates_creation(self):
        """Test creation of default templates."""
        # Create loader with non-existent directory
        empty_dir = Path(self.temp_dir) / "empty"
        loader = TemplateLoader(str(empty_dir))
        
        # Check that default templates were created
        assert empty_dir.exists()
        templates = loader.list_templates()
        
        # Should have default templates
        expected_templates = [
            "array_two_pointers", "string_manipulation", 
            "dynamic_programming", "tree_traversal", "default"
        ]
        
        for template in expected_templates:
            assert template in templates

class TestCodeAnalyzer:
    """Test cases for CodeAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer()
    
    def test_python_code_analysis(self):
        """Test Python code analysis."""
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
        
        analysis = self.analyzer.analyze_code(python_code, "python")
        
        assert analysis["language"] == "python"
        assert "dictionary" in analysis["data_structures"]
        assert analysis["time_complexity"] == "O(n)"
        assert analysis["space_complexity"] == "O(n)"
    
    def test_cpp_code_analysis(self):
        """Test C++ code analysis."""
        cpp_code = '''
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
        
        analysis = self.analyzer.analyze_code(cpp_code, "cpp")
        
        assert analysis["language"] == "cpp"
        assert "vector" in analysis["data_structures"]
        assert "hash_map" in analysis["data_structures"]
        assert analysis["time_complexity"] == "O(n)"
    
    def test_two_pointers_pattern_detection(self):
        """Test detection of two pointers pattern."""
        two_pointers_code = '''
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
        
        analysis = self.analyzer.analyze_code(two_pointers_code, "python")
        
        assert "Two Pointers" in analysis["patterns"]
        assert analysis["time_complexity"] == "O(n)"
        assert analysis["space_complexity"] == "O(1)"
    
    def test_dynamic_programming_detection(self):
        """Test detection of dynamic programming pattern."""
        dp_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]
'''
        
        analysis = self.analyzer.analyze_code(dp_code, "python")
        
        assert "Dynamic Programming" in analysis["patterns"]
        assert analysis["space_complexity"] == "O(n)"

class TestExplanationEngine:
    """Test cases for ExplanationEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.temp_dir) / "templates"
        self.engine = ExplanationEngine(str(self.templates_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_explanation_generation_with_template(self):
        """Test explanation generation using templates."""
        # The engine should create default templates
        explanation = self.engine.generate_explanation(
            problem_slug="two-sum",
            language="python",
            tags=["array", "hash-table"],
            difficulty="easy"
        )
        
        assert "two-sum" in explanation.lower()
        assert "python" in explanation.lower()
        assert len(explanation) > 100  # Should be substantial
    
    def test_explanation_with_code_analysis(self):
        """Test explanation generation with code analysis."""
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
        
        explanation = self.engine.generate_explanation(
            problem_slug="two-sum",
            language="python",
            code=python_code,
            tags=["array"],
            difficulty="easy"
        )
        
        assert "dictionary" in explanation.lower() or "hash" in explanation.lower()
        assert "O(n)" in explanation
        assert len(explanation) > 200
    
    def test_fallback_explanation(self):
        """Test fallback explanation when no template matches."""
        explanation = self.engine.generate_explanation(
            problem_slug="unknown-problem-xyz",
            language="python",
            tags=["unknown"],
            difficulty="hard"
        )
        
        # Should still generate some explanation
        assert "unknown-problem-xyz" in explanation
        assert "python" in explanation.lower()
        assert len(explanation) > 50
    
    def test_explanation_with_examples(self):
        """Test explanation generation with examples."""
        examples = [
            {
                "input": "[2,7,11,15], 9",
                "output": "[0,1]",
                "explanation": "2 + 7 = 9"
            }
        ]
        
        explanation = self.engine.explain_with_examples(
            problem_slug="two-sum",
            language="python",
            examples=examples
        )
        
        assert "Example" in explanation
        assert "[2,7,11,15]" in explanation
        assert "[0,1]" in explanation
    
    def test_hints_generation(self):
        """Test hint generation."""
        hints = self.engine.get_hints("two-sum", "easy")
        
        assert isinstance(hints, list)
        assert len(hints) > 0
        assert len(hints) <= 4  # Should limit to 4 hints
        
        # Should contain relevant hints for array problems
        hint_text = " ".join(hints).lower()
        assert any(keyword in hint_text for keyword in ["hash", "map", "pointer", "data structure"])

def run_all_tests():
    """Run all tests manually."""
    print("Running Template-Based Explanation System Tests...")
    print("=" * 60)
    
    test_classes = [TestTemplateLoader, TestCodeAnalyzer, TestExplanationEngine]
    
    for test_class in test_classes:
        print(f"\\nTesting {test_class.__name__}:")
        print("-" * 40)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            try:
                # Create instance and run setup
                instance = test_class()
                if hasattr(instance, 'setup_method'):
                    instance.setup_method()
                
                # Run test method
                test_method = getattr(instance, method_name)
                test_method()
                
                # Run teardown
                if hasattr(instance, 'teardown_method'):
                    instance.teardown_method()
                
                print(f"✓ {method_name}")
                
            except Exception as e:
                print(f"✗ {method_name}: {e}")
                import traceback
                traceback.print_exc()
    
    print("\\n" + "=" * 60)
    print("Template-based explanation system tests completed!")

if __name__ == "__main__":
    run_all_tests()