#!/usr/bin/env python3
"""
Demonstration script for string-based test generators.
"""

from orchestrator.testing.generators.string_generators import (
    StringTestGenerator, StringGeneratorConfig, StringPattern,
    CoverAllCharsGenerator, ReverseStringGenerator, UppercaseGenerator,
    LowercaseGenerator, PalindromeCheckGenerator, CharacterCountGenerator,
    StringLengthGenerator
)
from orchestrator.testing.generators.base import TestCaseType

def demo_basic_string_generation():
    """Demonstrate basic string generation."""
    print("=== Basic String Generation ===")
    
    config = StringGeneratorConfig(
        seed=42,
        num_cases=5,
        min_length=3,
        max_length=8,
        charset='lowercase'
    )
    
    generator = StringTestGenerator(config)
    test_cases = generator.generate_test_cases()
    
    print(f"Generated {len(test_cases)} string test cases:")
    for i, test_case in enumerate(test_cases):
        print(f"  Case {i+1}: '{test_case.input_data}' -> '{test_case.expected_output}'")
        print(f"    Length: {len(test_case.input_data)}")
    print()

def demo_different_charsets():
    """Demonstrate different character sets."""
    print("=== Different Character Sets ===")
    
    charsets = ['lowercase', 'uppercase', 'digits', 'alphanumeric']
    
    for charset in charsets:
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            min_length=5,
            max_length=5,
            charset=charset
        )
        
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        print(f"{charset.upper()} charset:")
        for test_case in test_cases:
            print(f"  '{test_case.input_data}'")
    print()

def demo_string_patterns():
    """Demonstrate different string patterns."""
    print("=== String Patterns ===")
    
    patterns = [
        StringPattern.PALINDROME,
        StringPattern.REPEATED,
        StringPattern.ALTERNATING,
        StringPattern.ASCENDING,
        StringPattern.DESCENDING
    ]
    
    for pattern in patterns:
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            min_length=4,
            max_length=6,
            patterns=[pattern]
        )
        
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        print(f"{pattern.value.upper()} pattern:")
        for test_case in test_cases:
            print(f"  '{test_case.input_data}'")
    print()

def demo_cover_all_chars():
    """Demonstrate character coverage generator."""
    print("=== Character Coverage Generator ===")
    
    config = StringGeneratorConfig(
        seed=42,
        num_cases=3,
        charset='abcde',
        min_length=2,
        max_length=4,
        ensure_coverage=True
    )
    
    generator = CoverAllCharsGenerator(config)
    test_cases = generator.generate_test_cases()
    
    print("Generated test cases:")
    for test_case in test_cases:
        print(f"  '{test_case.input_data}'")
    
    # Show coverage report
    report = generator.get_coverage_report()
    print(f"\nCoverage Report:")
    print(f"  Total characters: {report['total_characters']}")
    print(f"  Covered characters: {report['covered_characters']}")
    print(f"  Coverage percentage: {report['coverage_percentage']:.1f}%")
    print(f"  Covered chars: {report['covered_characters_list']}")
    if report['missing_characters']:
        print(f"  Missing chars: {report['missing_characters']}")
    print()

def demo_specific_generators():
    """Demonstrate specific string problem generators."""
    print("=== Specific String Problem Generators ===")
    
    # Reverse string generator
    print("REVERSE STRING:")
    config = StringGeneratorConfig(seed=42, num_cases=3, min_length=4, max_length=6)
    generator = ReverseStringGenerator(config)
    test_cases = generator.generate_test_cases()
    
    for test_case in test_cases:
        print(f"  '{test_case.input_data}' -> '{test_case.expected_output}'")
    
    # Uppercase generator
    print("\nUPPERCASE CONVERSION:")
    config = StringGeneratorConfig(seed=42, num_cases=3, charset='letters', min_length=4, max_length=6)
    generator = UppercaseGenerator(config)
    test_cases = generator.generate_test_cases()
    
    for test_case in test_cases:
        print(f"  '{test_case.input_data}' -> '{test_case.expected_output}'")
    
    # Palindrome check generator
    print("\nPALINDROME CHECK:")
    config = StringGeneratorConfig(
        seed=42, 
        num_cases=4, 
        patterns=[StringPattern.PALINDROME, StringPattern.RANDOM],
        min_length=3, 
        max_length=5
    )
    generator = PalindromeCheckGenerator(config)
    test_cases = generator.generate_test_cases()
    
    for test_case in test_cases:
        print(f"  '{test_case.input_data}' -> {test_case.expected_output}")
    
    # Character count generator
    print("\nCHARACTER COUNT:")
    config = StringGeneratorConfig(seed=42, num_cases=2, min_length=4, max_length=6)
    generator = CharacterCountGenerator(config)
    test_cases = generator.generate_test_cases()
    
    for test_case in test_cases:
        print(f"  '{test_case.input_data}' -> {test_case.expected_output}")
    
    # String length generator
    print("\nSTRING LENGTH:")
    config = StringGeneratorConfig(seed=42, num_cases=3, min_length=2, max_length=8)
    generator = StringLengthGenerator(config)
    test_cases = generator.generate_test_cases()
    
    for test_case in test_cases:
        print(f"  '{test_case.input_data}' -> {test_case.expected_output}")
    print()

def demo_edge_cases():
    """Demonstrate edge case generation."""
    print("=== Edge Case Generation ===")
    
    config = StringGeneratorConfig(
        seed=42,
        num_cases=6,
        case_types=[TestCaseType.EDGE],
        min_length=1,
        max_length=10,
        patterns=[StringPattern.PALINDROME, StringPattern.ALTERNATING]
    )
    
    generator = StringTestGenerator(config)
    test_cases = generator.generate_test_cases()
    
    print("Edge cases:")
    for test_case in test_cases:
        print(f"  '{test_case.input_data}' (length: {len(test_case.input_data)})")
        print(f"    Description: {test_case.description}")
    print()

def demo_deterministic_generation():
    """Demonstrate deterministic generation."""
    print("=== Deterministic Generation ===")
    
    config = StringGeneratorConfig(
        seed=123,
        num_cases=3,
        min_length=4,
        max_length=6,
        charset='abc'
    )
    
    # Generate twice with same config
    generator1 = StringTestGenerator(config)
    test_cases1 = generator1.generate_test_cases()
    
    generator2 = StringTestGenerator(config)
    test_cases2 = generator2.generate_test_cases()
    
    print("First generation:")
    for tc in test_cases1:
        print(f"  '{tc.input_data}'")
    
    print("Second generation (should be identical):")
    for tc in test_cases2:
        print(f"  '{tc.input_data}'")
    
    # Verify they're identical
    identical = all(
        tc1.input_data == tc2.input_data 
        for tc1, tc2 in zip(test_cases1, test_cases2)
    )
    print(f"Generations are identical: {identical}")
    print()

def demo_mixed_patterns():
    """Demonstrate mixed pattern generation."""
    print("=== Mixed Pattern Generation ===")
    
    config = StringGeneratorConfig(
        seed=42,
        num_cases=8,
        min_length=4,
        max_length=8,
        patterns=[
            StringPattern.PALINDROME,
            StringPattern.REPEATED,
            StringPattern.RANDOM,
            StringPattern.ALTERNATING
        ]
    )
    
    generator = StringTestGenerator(config)
    test_cases = generator.generate_test_cases()
    
    print("Mixed pattern test cases:")
    for test_case in test_cases:
        print(f"  '{test_case.input_data}' - {test_case.description}")
    print()

def demo_custom_charset():
    """Demonstrate custom character set."""
    print("=== Custom Character Set ===")
    
    config = StringGeneratorConfig(
        seed=42,
        num_cases=5,
        min_length=3,
        max_length=6,
        charset='!@#$%'  # Custom special characters
    )
    
    generator = StringTestGenerator(config)
    test_cases = generator.generate_test_cases()
    
    print("Custom charset (!@#$%) test cases:")
    for test_case in test_cases:
        print(f"  '{test_case.input_data}'")
    print()

def main():
    """Run all demonstrations."""
    print("String-Based Test Generators Demonstration\n")
    
    demo_basic_string_generation()
    demo_different_charsets()
    demo_string_patterns()
    demo_cover_all_chars()
    demo_specific_generators()
    demo_edge_cases()
    demo_deterministic_generation()
    demo_mixed_patterns()
    demo_custom_charset()
    
    print("Demo completed!")

if __name__ == "__main__":
    main()