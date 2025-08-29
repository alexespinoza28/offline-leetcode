#!/usr/bin/env python3
"""
Demo script showcasing community explanation integration.

This demonstrates the complete community explanation workflow including:
- Community explanation loading and priority system
- Integration with template-based explanations
- Metadata extraction and statistics
- Enhancement with code analysis
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from explain.engine import ExplanationEngine
from explain.community_loader import CommunityExplanationLoader

def create_sample_problems(problems_dir: Path):
    """Create sample problems with community explanations."""
    
    # Problem 1: Comprehensive community explanation
    two_sum_dir = problems_dir / "two-sum"
    two_sum_dir.mkdir(parents=True)
    
    two_sum_explanation = '''---
title: Two Sum
author: community-expert
difficulty: easy
tags: [array, hash-table]
created: 2024-01-15
has_code_examples: true
has_complexity_analysis: true
has_step_by_step: true
---

# Two Sum - Community Solution Explanation

## Problem Understanding

Given an array of integers `nums` and an integer `target`, we need to find two numbers in the array that add up to the target value and return their indices.

## Approach

The key insight is to use a **hash map** to store numbers we've seen along with their indices. For each number, we check if its complement (target - current number) exists in our hash map.

### Why Hash Map?

- **O(1) average lookup time** - much faster than nested loops
- **Single pass solution** - we only need to iterate through the array once
- **Space-time tradeoff** - we use O(n) extra space to achieve O(n) time complexity

## Algorithm Steps

1. **Initialize** an empty hash map to store {number: index} pairs
2. **Iterate** through the array with both index and value
3. **Calculate** the complement: `complement = target - current_number`
4. **Check** if complement exists in hash map
   - If yes: return [complement_index, current_index]
   - If no: store current number and index in hash map
5. **Continue** until solution is found

## Implementation

```python
def two_sum(nums, target):
    """
    Find two numbers that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
        
    Returns:
        List of two indices [i, j] where nums[i] + nums[j] == target
    """
    num_to_index = {}  # Hash map: number -> index
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in num_to_index:
            return [num_to_index[complement], i]
        
        num_to_index[num] = i
    
    return []  # No solution found (shouldn't happen per problem constraints)
```

## Complexity Analysis

- **Time Complexity**: O(n)
  - Single pass through the array
  - Hash map operations (insert/lookup) are O(1) average case
  
- **Space Complexity**: O(n)
  - In worst case, we store all n numbers in the hash map
  - This happens when the solution is the last two elements

## Example Walkthrough

Let's trace through `nums = [2, 7, 11, 15]`, `target = 9`:

```
Initial: num_to_index = {}, target = 9

i=0, num=2:
  complement = 9 - 2 = 7
  7 not in num_to_index
  num_to_index = {2: 0}

i=1, num=7:
  complement = 9 - 7 = 2
  2 is in num_to_index at index 0
  return [0, 1] ✓
```

## Key Insights

- **Hash maps are perfect for "find the complement" problems**
- **Single pass is possible** when we store information as we go
- **Order matters**: we return the first valid pair we find
- **No duplicate indices**: the problem guarantees exactly one solution

## Alternative Approaches

### Brute Force O(n²)
```python
def two_sum_brute_force(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
```

### Two Pointers (only works on sorted arrays)
```python
def two_sum_sorted(nums, target):
    # This modifies the problem since we need original indices
    indexed_nums = [(num, i) for i, num in enumerate(nums)]
    indexed_nums.sort()
    
    left, right = 0, len(nums) - 1
    while left < right:
        current_sum = indexed_nums[left][0] + indexed_nums[right][0]
        if current_sum == target:
            return sorted([indexed_nums[left][1], indexed_nums[right][1]])
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return []
```

## Common Pitfalls

- **Using the same element twice**: Make sure to check `i != j`
- **Returning values instead of indices**: Problem asks for indices, not values
- **Not handling edge cases**: Empty array, single element, no solution
- **Assuming sorted input**: The array is not necessarily sorted

## Related Problems

- **3Sum**: Extension to finding three numbers that sum to target
- **4Sum**: Finding four numbers that sum to target  
- **Two Sum II**: When the input array is sorted
- **Two Sum III**: Design a data structure for two sum queries

## Practice Tips

1. **Start with brute force** to understand the problem
2. **Identify the bottleneck** (nested loops in this case)
3. **Think about data structures** that can speed up lookups
4. **Consider space-time tradeoffs** (more space for less time)
5. **Test with edge cases** and trace through examples
'''
    
    (two_sum_dir / "explanation.md").write_text(two_sum_explanation, encoding='utf-8')
    
    # Problem 2: Basic community explanation
    reverse_string_dir = problems_dir / "reverse-string"
    reverse_string_dir.mkdir(parents=True)
    
    reverse_string_explanation = '''---
title: Reverse String
author: beginner-contributor
difficulty: easy
tags: [string, two-pointers]
---

# Reverse String - Simple Explanation

## Problem
Reverse a string in-place using O(1) extra space.

## Solution
Use two pointers - one at start, one at end. Swap characters and move pointers toward center.

```python
def reverse_string(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
```

## Why This Works
- Two pointers meet in the middle
- Each swap fixes two positions
- O(n/2) swaps = O(n) time
- No extra space needed
'''
    
    (reverse_string_dir / "explanation.md").write_text(reverse_string_explanation, encoding='utf-8')
    
    # Problem 3: No community explanation (will use template)
    fibonacci_dir = problems_dir / "fibonacci"
    fibonacci_dir.mkdir(parents=True)
    # No explanation.md file - will fallback to template

def demonstrate_community_loading():
    """Demonstrate community explanation loading."""
    print("COMMUNITY EXPLANATION LOADING")
    print("=" * 50)
    
    # Create temporary problems directory
    temp_dir = tempfile.mkdtemp()
    problems_dir = Path(temp_dir) / "problems"
    
    try:
        # Create sample problems
        create_sample_problems(problems_dir)
        
        # Create community loader
        loader = CommunityExplanationLoader(str(problems_dir))
        
        print(f"Problems directory: {problems_dir}")
        
        # List problems with explanations
        problems_with_explanations = loader.list_problems_with_explanations()
        print(f"\\nProblems with community explanations: {problems_with_explanations}")
        
        # Load and show explanation details
        for problem in problems_with_explanations:
            print(f"\\n--- {problem.upper()} ---")
            explanation_data = loader.load_community_explanation(problem)
            
            if explanation_data:
                metadata = explanation_data['metadata']
                print(f"Author: {metadata.get('author', 'Unknown')}")
                print(f"Word count: {metadata.get('word_count', 0)}")
                print(f"Reading time: {metadata.get('estimated_reading_time', 0)} minutes")
                print(f"Has code examples: {metadata.get('has_code_examples', False)}")
                print(f"Has complexity analysis: {metadata.get('has_complexity_analysis', False)}")
                print(f"Priority score: {loader.get_explanation_priority(problem)}")
        
        # Show statistics
        print("\\n--- COMMUNITY EXPLANATION STATISTICS ---")
        stats = loader.get_explanation_stats()
        print(f"Total problems with explanations: {stats['total_problems_with_explanations']}")
        
        return problems_dir
        
    except Exception as e:
        print(f"Error in community loading demo: {e}")
        shutil.rmtree(temp_dir)
        return None

def demonstrate_priority_system(problems_dir):
    """Demonstrate the priority system between community and template explanations."""
    print("\\n\\nPRIORITY SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    if not problems_dir:
        print("Skipping priority system demo - problems directory not available")
        return
    
    # Create explanation engine with both community and template support
    engine = ExplanationEngine(problems_dir=str(problems_dir))
    
    test_problems = [
        ("two-sum", "Has comprehensive community explanation"),
        ("reverse-string", "Has basic community explanation"), 
        ("fibonacci", "No community explanation - uses template"),
        ("unknown-problem", "No community or specific template - uses default")
    ]
    
    print("\\nExplanation Source Priority:")
    print("-" * 30)
    
    for problem, description in test_problems:
        source = engine.get_explanation_source(problem)
        print(f"{problem:20} → {source:10} ({description})")

def demonstrate_explanation_generation(problems_dir):
    """Demonstrate explanation generation with community integration."""
    print("\\n\\nEXPLANATION GENERATION WITH COMMUNITY INTEGRATION")
    print("=" * 60)
    
    if not problems_dir:
        print("Skipping explanation generation demo")
        return
    
    engine = ExplanationEngine(problems_dir=str(problems_dir))
    
    # Test cases
    test_cases = [
        {
            "problem": "two-sum",
            "description": "Community explanation with code analysis enhancement",
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
            "description": "Basic community explanation",
            "code": None
        },
        {
            "problem": "fibonacci",
            "description": "Template-based explanation (no community)",
            "code": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n{i}. {test_case['problem'].upper()}")
        print(f"   Description: {test_case['description']}")
        print("-" * 60)
        
        explanation = engine.generate_explanation(
            problem_slug=test_case['problem'],
            language="python",
            code=test_case['code']
        )
        
        # Show preview of explanation
        preview = explanation[:400] + "..." if len(explanation) > 400 else explanation
        print(preview)
        print(f"\\n[Full explanation length: {len(explanation)} characters]")

def demonstrate_template_creation():
    """Demonstrate creating explanation templates for community contribution."""
    print("\\n\\nCOMMUNITY EXPLANATION TEMPLATE CREATION")
    print("=" * 50)
    
    loader = CommunityExplanationLoader()
    
    # Create template for new problem
    template = loader.create_explanation_template(
        "binary-search", 
        "Binary Search"
    )
    
    print("Generated template for community contribution:")
    print("-" * 40)
    print(template[:800] + "..." if len(template) > 800 else template)

def main():
    """Main demonstration function."""
    print("COMMUNITY EXPLANATION INTEGRATION DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how community explanations integrate with the")
    print("template-based explanation system with priority handling.\\n")
    
    try:
        # Run demonstrations
        problems_dir = demonstrate_community_loading()
        demonstrate_priority_system(problems_dir)
        demonstrate_explanation_generation(problems_dir)
        demonstrate_template_creation()
        
        print("\\n" + "=" * 60)
        print("✓ DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("The community explanation integration provides:")
        print("• Priority system favoring community explanations")
        print("• Automatic metadata extraction and analysis")
        print("• Enhancement with code analysis when needed")
        print("• Fallback to template system when no community explanation exists")
        print("• Statistics and management of community contributions")
        print("• Template generation for new community explanations")
        
        # Clean up
        if problems_dir:
            shutil.rmtree(problems_dir.parent)
        
    except Exception as e:
        print(f"\\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()