#!/usr/bin/env python3
"""
Tests for community explanation integration.
"""

import tempfile
import shutil
import sys
from pathlib import Path

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from explain.community_loader import CommunityExplanationLoader
from explain.engine import ExplanationEngine

class TestCommunityExplanationLoader:
    """Test cases for CommunityExplanationLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.problems_dir = Path(self.temp_dir) / "problems"
        self.problems_dir.mkdir(parents=True)
        self.loader = CommunityExplanationLoader(str(self.problems_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_problem_with_explanation(self, problem_slug: str, explanation_content: str):
        """Create a problem directory with explanation.md file."""
        problem_dir = self.problems_dir / problem_slug
        problem_dir.mkdir(parents=True)
        
        explanation_file = problem_dir / "explanation.md"
        explanation_file.write_text(explanation_content, encoding='utf-8')
        
        return explanation_file
    
    def test_find_community_explanation(self):
        """Test finding community explanation files."""
        # Create explanation file
        explanation_content = "# Test Explanation\\n\\nThis is a test explanation."
        self.create_problem_with_explanation("test-problem", explanation_content)
        
        # Test finding explanation
        explanation_path = self.loader.find_community_explanation("test-problem")
        assert explanation_path is not None
        assert explanation_path.exists()
        assert explanation_path.name == "explanation.md"
        
        # Test non-existent problem
        no_explanation = self.loader.find_community_explanation("non-existent")
        assert no_explanation is None
    
    def test_load_community_explanation_simple(self):
        """Test loading simple community explanation."""
        explanation_content = "# Simple Explanation\\n\\nThis is a simple explanation without metadata."
        self.create_problem_with_explanation("simple-problem", explanation_content)
        
        # Load explanation
        explanation_data = self.loader.load_community_explanation("simple-problem")
        
        assert explanation_data is not None
        assert explanation_data['content'] == explanation_content
        assert explanation_data['source'] == 'community'
        assert explanation_data['metadata']['source'] == 'community'
        assert 'word_count' in explanation_data['metadata']
    
    def test_load_community_explanation_with_metadata(self):
        """Test loading community explanation with front matter metadata."""
        explanation_content = '''---
title: Test Problem
author: community
difficulty: easy
tags: [array, hash-table]
has_code_examples: true
---

# Test Problem Explanation

This is a comprehensive explanation with metadata.

## Algorithm

The algorithm works by...

```python
def solution():
    return "test"
```

## Complexity

Time: O(n), Space: O(1)
'''
        
        self.create_problem_with_explanation("metadata-problem", explanation_content)
        
        # Load explanation
        explanation_data = self.loader.load_community_explanation("metadata-problem")
        
        assert explanation_data is not None
        assert explanation_data['metadata']['title'] == 'Test Problem'
        assert explanation_data['metadata']['author'] == 'community'
        assert explanation_data['metadata']['difficulty'] == 'easy'
        assert explanation_data['metadata']['tags'] == ['array', 'hash-table']
        assert explanation_data['metadata']['has_code_examples'] == True
        
        # Content should not include front matter
        assert '---' not in explanation_data['content']
        assert 'Test Problem Explanation' in explanation_data['content']
    
    def test_metadata_extraction_from_content(self):
        """Test automatic metadata extraction from content."""
        explanation_content = '''# Algorithm Explanation

This explanation includes code examples and complexity analysis.

```python
def two_sum(nums, target):
    return []
```

Time Complexity: O(n)
Space Complexity: O(1)

Step 1: Initialize variables
Step 2: Process array
'''
        
        self.create_problem_with_explanation("auto-metadata", explanation_content)
        
        # Load explanation
        explanation_data = self.loader.load_community_explanation("auto-metadata")
        
        metadata = explanation_data['metadata']
        assert metadata['has_code_examples'] == True
        assert metadata['has_complexity_analysis'] == True
        assert metadata['has_step_by_step'] == True
        assert metadata['word_count'] > 0
        assert metadata['estimated_reading_time'] >= 1
    
    def test_explanation_priority_calculation(self):
        """Test priority calculation for community explanations."""
        # Create comprehensive explanation
        comprehensive_content = '''---
author: expert
---

# Comprehensive Explanation

This is a detailed explanation with code examples and complexity analysis.

```python
def solution():
    pass
```

Time Complexity: O(n)

Step 1: Do this
Step 2: Do that
''' + ' '.join(['word'] * 600)  # Make it long
        
        self.create_problem_with_explanation("comprehensive", comprehensive_content)
        
        # Create basic explanation
        basic_content = "# Basic Explanation\\n\\nThis is basic."
        self.create_problem_with_explanation("basic", basic_content)
        
        # Test priorities
        comprehensive_priority = self.loader.get_explanation_priority("comprehensive")
        basic_priority = self.loader.get_explanation_priority("basic")
        
        assert comprehensive_priority > basic_priority
        assert comprehensive_priority > 100  # Should have bonuses
        assert basic_priority == 100  # Base priority only
    
    def test_list_problems_with_explanations(self):
        """Test listing problems with community explanations."""
        # Create multiple problems with explanations
        problems = ["problem-1", "problem-2", "problem-3"]
        for problem in problems:
            self.create_problem_with_explanation(problem, f"# {problem} explanation")
        
        # Create problem without explanation
        problem_without = self.problems_dir / "no-explanation"
        problem_without.mkdir()
        
        # Test listing
        problems_with_explanations = self.loader.list_problems_with_explanations()
        
        assert len(problems_with_explanations) == 3
        for problem in problems:
            assert problem in problems_with_explanations
        assert "no-explanation" not in problems_with_explanations
    
    def test_explanation_stats(self):
        """Test getting explanation statistics."""
        # Create explanations with different characteristics
        explanations = {
            "detailed": '''---
has_code_examples: true
---
# Detailed
``` python
code here
```
Time: O(n)
Step 1: Do this
''' + ' '.join(['word'] * 300),
            
            "basic": "# Basic\\nSimple explanation."
        }
        
        for problem, content in explanations.items():
            self.create_problem_with_explanation(problem, content)
        
        # Get stats
        stats = self.loader.get_explanation_stats()
        
        assert stats['total_problems_with_explanations'] == 2
        assert 'detailed' in stats['problems']
        assert 'basic' in stats['problems']
        
        # Check detailed stats
        detailed_stats = stats['explanation_details']['detailed']
        assert detailed_stats['has_code_examples'] == True
        assert detailed_stats['word_count'] > 300
        assert detailed_stats['priority'] > 100
        
        basic_stats = stats['explanation_details']['basic']
        assert basic_stats['has_code_examples'] == False
        assert basic_stats['word_count'] < 50
    
    def test_create_explanation_template(self):
        """Test creating explanation template."""
        template = self.loader.create_explanation_template("new-problem", "New Problem")
        
        assert "New Problem" in template
        assert "---" in template  # Has front matter
        assert "## Problem Understanding" in template
        assert "## Approach" in template
        assert "## Implementation" in template
        assert "## Complexity Analysis" in template
        assert "```python" in template
    
    def test_cache_functionality(self):
        """Test explanation caching."""
        explanation_content = "# Cached Explanation\\n\\nThis should be cached."
        explanation_file = self.create_problem_with_explanation("cached-problem", explanation_content)
        
        # Load explanation (should cache it)
        explanation1 = self.loader.load_community_explanation("cached-problem")
        
        # Modify file on disk
        explanation_file.write_text("# Modified Explanation\\n\\nThis is modified.", encoding='utf-8')
        
        # Load again (should return cached version)
        explanation2 = self.loader.load_community_explanation("cached-problem")
        assert explanation1['content'] == explanation2['content']
        assert "Modified" not in explanation2['content']
        
        # Reload bypassing cache
        explanation3 = self.loader.reload_explanation("cached-problem")
        assert "Modified" in explanation3['content']
        
        # Clear cache and load
        self.loader.clear_cache()
        explanation4 = self.loader.load_community_explanation("cached-problem")
        assert "Modified" in explanation4['content']

class TestExplanationEngineIntegration:
    """Test integration of community explanations with ExplanationEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.problems_dir = Path(self.temp_dir) / "problems"
        self.problems_dir.mkdir(parents=True)
        self.engine = ExplanationEngine(problems_dir=str(self.problems_dir))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_community_explanation(self, problem_slug: str, content: str):
        """Create community explanation for testing."""
        problem_dir = self.problems_dir / problem_slug
        problem_dir.mkdir(parents=True)
        
        explanation_file = problem_dir / "explanation.md"
        explanation_file.write_text(content, encoding='utf-8')
    
    def test_community_explanation_priority(self):
        """Test that community explanations take priority over templates."""
        # Create community explanation
        community_content = '''---
author: community-expert
---

# Community Two Sum Explanation

This is a community-contributed explanation that should take priority.

## Algorithm
Use a hash map for O(1) lookups.
'''
        
        self.create_community_explanation("two-sum", community_content)
        
        # Generate explanation
        explanation = self.engine.generate_explanation(
            problem_slug="two-sum",
            language="python",
            tags=["array", "hash-table"]
        )
        
        # Should use community explanation
        assert "Community Explanation" in explanation
        assert "community-expert" in explanation
        assert "Community Two Sum Explanation" in explanation
    
    def test_template_fallback(self):
        """Test fallback to template when no community explanation exists."""
        # Generate explanation for problem without community explanation
        explanation = self.engine.generate_explanation(
            problem_slug="unknown-problem",
            language="python",
            tags=["array"]
        )
        
        # Should use template-based explanation
        assert len(explanation) > 100
        assert "Algorithm Overview" in explanation or "Solution Explanation" in explanation
    
    def test_explanation_source_detection(self):
        """Test detection of explanation source."""
        # Create community explanation
        self.create_community_explanation("community-problem", "# Community explanation")
        
        # Test source detection
        assert self.engine.get_explanation_source("community-problem") == "community"
        assert self.engine.get_explanation_source("two-sum") == "template"  # Should match template
        assert self.engine.get_explanation_source("unknown-xyz") == "fallback"
    
    def test_community_explanation_enhancement(self):
        """Test enhancement of community explanations with code analysis."""
        # Create basic community explanation without code examples
        basic_community = '''# Basic Community Explanation

This explanation doesn't have code examples or complexity analysis.
'''
        
        self.create_community_explanation("basic-community", basic_community)
        
        # Generate explanation with code
        python_code = '''
def solution(nums, target):
    num_dict = {}
    for i, num in enumerate(nums):
        if target - num in num_dict:
            return [num_dict[target - num], i]
        num_dict[num] = i
    return []
'''
        
        explanation = self.engine.generate_explanation(
            problem_slug="basic-community",
            language="python",
            code=python_code
        )
        
        # Should enhance with code analysis
        assert "Community Explanation" in explanation
        assert "Code Analysis" in explanation
        assert "Time Complexity" in explanation
        assert "dictionary" in explanation.lower()
    
    def test_community_stats_integration(self):
        """Test integration of community explanation statistics."""
        # Create multiple community explanations
        explanations = {
            "detailed-community": '''---
author: expert
---
# Detailed
```python
code
```
Time: O(n)
''' + ' '.join(['word'] * 400),
            
            "simple-community": "# Simple\\nBasic explanation."
        }
        
        for problem, content in explanations.items():
            self.create_community_explanation(problem, content)
        
        # Test stats
        problems_list = self.engine.list_problems_with_community_explanations()
        assert len(problems_list) == 2
        assert "detailed-community" in problems_list
        assert "simple-community" in problems_list
        
        stats = self.engine.get_community_explanation_stats()
        assert stats['total_problems_with_explanations'] == 2
        assert 'detailed-community' in stats['explanation_details']
        assert 'simple-community' in stats['explanation_details']

def run_all_tests():
    """Run all community explanation tests."""
    print("Running Community Explanation Integration Tests...")
    print("=" * 60)
    
    test_classes = [TestCommunityExplanationLoader, TestExplanationEngineIntegration]
    
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
    print("Community explanation integration tests completed!")

if __name__ == "__main__":
    run_all_tests()