#!/usr/bin/env python3
"""
Show a complete example of the template-based explanation system output.
"""

import sys
from pathlib import Path

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from explain.engine import ExplanationEngine

def show_explanation_example():
    """Show a complete explanation example."""
    print("TEMPLATE-BASED EXPLANATION SYSTEM EXAMPLE")
    print("=" * 60)
    
    # Create explanation engine
    engine = ExplanationEngine()
    
    # Example code
    two_sum_code = '''
def two_sum(nums, target):
    """
    Find two numbers in the array that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
        
    Returns:
        List of two indices that add up to target
    """
    num_dict = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in num_dict:
            return [num_dict[complement], i]
        
        num_dict[num] = i
    
    return []  # No solution found
'''
    
    print("\\nInput Code:")
    print("-" * 30)
    print(two_sum_code)
    
    print("\\nGenerated Explanation:")
    print("-" * 30)
    
    # Generate explanation
    explanation = engine.generate_explanation(
        problem_slug="two-sum",
        language="python",
        code=two_sum_code,
        tags=["array", "hash-table"],
        difficulty="easy"
    )
    
    print(explanation)
    
    print("\\n" + "=" * 60)
    print("This explanation was automatically generated using:")
    print("• Pattern-based template selection")
    print("• Code analysis and complexity estimation")
    print("• Variable substitution in markdown templates")
    print("• Multi-language algorithm pattern detection")

if __name__ == "__main__":
    show_explanation_example()