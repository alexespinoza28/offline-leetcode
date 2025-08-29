#!/usr/bin/env python3
"""
Demonstration script for the output comparison system.
"""

from orchestrator.testing.comparators import (
    TextExactComparator,
    NumericComparator,
    JsonComparator,
    ArrayComparator,
    ComparatorFactory
)

def demo_text_comparator():
    """Demonstrate text comparison."""
    print("=== Text Comparator Demo ===")
    comparator = TextExactComparator(normalize_whitespace=True)
    
    # Exact match
    result = comparator.compare("Hello World", "Hello World")
    print(f"Exact match: {result.result.value} (similarity: {result.similarity_score:.2f})")
    
    # Whitespace normalization
    result = comparator.compare("Hello   World\n", "Hello World")
    print(f"Whitespace normalized: {result.result.value} (similarity: {result.similarity_score:.2f})")
    
    # Mismatch with diff
    result = comparator.compare("Hello World", "Hello Universe")
    print(f"Mismatch: {result.result.value} (similarity: {result.similarity_score:.2f})")
    print(f"Diff:\n{result.diff}")
    print()

def demo_numeric_comparator():
    """Demonstrate numeric comparison."""
    print("=== Numeric Comparator Demo ===")
    comparator = NumericComparator(epsilon=1e-6)
    
    # Exact match
    result = comparator.compare("3.14159", "3.14159")
    print(f"Exact match: {result.result.value}")
    
    # Within tolerance
    result = comparator.compare("3.14159", "3.141591")
    print(f"Within tolerance: {result.result.value}")
    
    # Multiple numbers
    result = comparator.compare("1.5 2.7 3.14", "1.5 2.7 3.14")
    print(f"Multiple numbers: {result.result.value}")
    print(f"Parsed numbers: {result.expected_parsed}")
    
    # Mismatch
    result = comparator.compare("3.14159", "2.71828")
    print(f"Mismatch: {result.result.value}")
    print(f"Diff:\n{result.diff}")
    print()

def demo_json_comparator():
    """Demonstrate JSON comparison."""
    print("=== JSON Comparator Demo ===")
    comparator = JsonComparator(ignore_order=True)
    
    # Order independence
    json1 = '{"name": "John", "age": 30}'
    json2 = '{"age": 30, "name": "John"}'
    result = comparator.compare(json1, json2)
    print(f"Order independent: {result.result.value}")
    
    # Nested structure mismatch
    json1 = '{"user": {"name": "John", "age": 30}}'
    json2 = '{"user": {"name": "John", "age": 31}}'
    result = comparator.compare(json1, json2)
    print(f"Nested mismatch: {result.result.value}")
    print(f"Diff:\n{result.diff}")
    print()

def demo_array_comparator():
    """Demonstrate array comparison."""
    print("=== Array Comparator Demo ===")
    comparator = ArrayComparator(ignore_order=False)
    
    # Exact match
    result = comparator.compare("[1, 2, 3]", "[1, 2, 3]")
    print(f"Exact match: {result.result.value}")
    
    # Different brackets
    comparator_flexible = ArrayComparator(ignore_brackets=True)
    result = comparator_flexible.compare("[1, 2, 3]", "(1, 2, 3)")
    print(f"Different brackets: {result.result.value}")
    
    # Order matters
    result = comparator.compare("[1, 2, 3]", "[3, 1, 2]")
    print(f"Order matters: {result.result.value}")
    
    # Order independent
    comparator_unordered = ArrayComparator(ignore_order=True)
    result = comparator_unordered.compare("[1, 2, 3]", "[3, 1, 2]")
    print(f"Order independent: {result.result.value}")
    print()

def demo_auto_detection():
    """Demonstrate auto-detection."""
    print("=== Auto-Detection Demo ===")
    
    test_cases = [
        ("3.14159", "2.71828", "Numeric"),
        ("[1, 2, 3]", "[1, 2, 3]", "Array"),
        ('{"key": "value"}', '{"key": "value"}', "JSON"),
        ("Hello World", "Hello Universe", "Text")
    ]
    
    for expected, actual, expected_type in test_cases:
        comparator = ComparatorFactory.auto_detect_comparator(expected, actual)
        result = comparator.compare(expected, actual)
        print(f"{expected_type}: {comparator.get_name()} -> {result.result.value}")
    print()

def main():
    """Run all demonstrations."""
    print("Output Comparison System Demonstration\n")
    
    demo_text_comparator()
    demo_numeric_comparator()
    demo_json_comparator()
    demo_array_comparator()
    demo_auto_detection()
    
    print("Demo completed!")

if __name__ == "__main__":
    main()