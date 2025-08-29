#!/usr/bin/env python3
"""
Demonstration script for the test generator framework.
"""

from orchestrator.testing.generators.base import (
    GeneratorConfig, TestCaseType, SimpleTestGenerator
)
from orchestrator.testing.generators.constraints import (
    RangeConstraint, LengthConstraint, CharsetConstraint, 
    ConstraintValidator
)

def demo_basic_generation():
    """Demonstrate basic test case generation."""
    print("=== Basic Test Generation ===")
    
    config = GeneratorConfig(
        seed=42,
        num_cases=5,
        problem_id='demo-problem'
    )
    
    generator = SimpleTestGenerator(config)
    test_cases = generator.generate_test_cases()
    
    print(f"Generated {len(test_cases)} test cases:")
    for i, test_case in enumerate(test_cases):
        print(f"  Case {i+1}: {test_case.input_data} -> {test_case.expected_output}")
        print(f"    Seed: {test_case.metadata['seed']}")
    print()

def demo_deterministic_generation():
    """Demonstrate deterministic generation."""
    print("=== Deterministic Generation ===")
    
    config = GeneratorConfig(seed=123, num_cases=3, problem_id='deterministic-test')
    
    # Generate twice with same config
    generator1 = SimpleTestGenerator(config)
    test_cases1 = generator1.generate_test_cases()
    
    generator2 = SimpleTestGenerator(config)
    test_cases2 = generator2.generate_test_cases()
    
    print("First generation:")
    for tc in test_cases1:
        print(f"  {tc.input_data} -> {tc.expected_output}")
    
    print("Second generation (should be identical):")
    for tc in test_cases2:
        print(f"  {tc.input_data} -> {tc.expected_output}")
    
    # Verify they're identical
    identical = all(
        tc1.input_data == tc2.input_data and tc1.expected_output == tc2.expected_output
        for tc1, tc2 in zip(test_cases1, test_cases2)
    )
    print(f"Generations are identical: {identical}")
    print()

def demo_constraints():
    """Demonstrate constraint-based generation."""
    print("=== Constraint-Based Generation ===")
    
    config = GeneratorConfig(
        seed=42,
        num_cases=8,
        constraints={
            'min_value': 10,
            'max_value': 20
        }
    )
    
    generator = SimpleTestGenerator(config)
    test_cases = generator.generate_test_cases()
    
    print("Generated test cases with constraints (min=10, max=20):")
    for test_case in test_cases:
        print(f"  {test_case.input_data} -> {test_case.expected_output}")
        # Verify constraint
        assert 10 <= test_case.input_data <= 20, f"Constraint violation: {test_case.input_data}"
    
    print("All test cases satisfy constraints ✓")
    print()

def demo_multiple_case_types():
    """Demonstrate multiple case types."""
    print("=== Multiple Case Types ===")
    
    config = GeneratorConfig(
        seed=42,
        num_cases=8,
        case_types=[TestCaseType.UNIT, TestCaseType.EDGE, TestCaseType.STRESS]
    )
    
    generator = SimpleTestGenerator(config)
    test_cases = generator.generate_test_cases()
    
    # Group by case type
    by_type = {}
    for test_case in test_cases:
        case_type = test_case.case_type
        if case_type not in by_type:
            by_type[case_type] = []
        by_type[case_type].append(test_case)
    
    for case_type, cases in by_type.items():
        print(f"{case_type.value.upper()} cases ({len(cases)}):")
        for test_case in cases:
            print(f"  {test_case.input_data} -> {test_case.expected_output}")
    print()

def demo_edge_cases():
    """Demonstrate edge case generation."""
    print("=== Edge Case Generation ===")
    
    config = GeneratorConfig(
        seed=42,
        num_cases=4,
        case_types=[TestCaseType.EDGE]
    )
    
    generator = SimpleTestGenerator(config)
    test_cases = generator.generate_test_cases()
    edge_cases = generator.generate_edge_cases()
    
    print("Generated edge cases:")
    for test_case in test_cases:
        print(f"  {test_case.input_data} -> {test_case.expected_output} ({test_case.description})")
    
    print("\nPredefined edge cases:")
    for test_case in edge_cases:
        print(f"  {test_case.input_data} -> {test_case.expected_output} ({test_case.description})")
    print()

def demo_constraints_validation():
    """Demonstrate constraint validation."""
    print("=== Constraint Validation ===")
    
    # Create some constraints
    constraints = [
        RangeConstraint(min_value=1, max_value=100),
        LengthConstraint(min_length=2, max_length=5)
    ]
    
    validator = ConstraintValidator(constraints)
    
    test_values = [
        [50, 75],      # Valid
        [0, 50],       # Range violation (0 < 1)
        [50, 150],     # Range violation (150 > 100)
        [50],          # Length violation (length < 2)
        [1, 2, 3, 4, 5, 6],  # Length violation (length > 5)
    ]
    
    print("Testing constraint validation:")
    for value in test_values:
        is_valid = validator.validate(value)
        violations = validator.get_violations(value)
        
        print(f"  {value}: {'✓' if is_valid else '✗'}")
        if violations:
            for violation in violations:
                print(f"    - {violation}")
    print()

def demo_random_utilities():
    """Demonstrate random utility methods."""
    print("=== Random Utilities ===")
    
    config = GeneratorConfig(seed=42)
    generator = SimpleTestGenerator(config)
    
    print("Random integer (1-10):", generator.generate_random_int(1, 10))
    print("Random float (1.0-10.0):", generator.generate_random_float(1.0, 10.0))
    print("Random choice from ['A', 'B', 'C']:", generator.generate_random_choice(['A', 'B', 'C']))
    print("Random sample of 3 from [1,2,3,4,5]:", generator.generate_random_sample([1,2,3,4,5], 3))
    print("Random string (length 8):", generator.generate_random_string(8))
    print("Random string with digits:", generator.generate_random_string(5, '0123456789'))
    
    original = [1, 2, 3, 4, 5]
    shuffled = generator.shuffle_list(original)
    print(f"Shuffled {original} -> {shuffled}")
    print()

def demo_generation_summary():
    """Demonstrate generation summary."""
    print("=== Generation Summary ===")
    
    config = GeneratorConfig(
        seed=123,
        num_cases=10,
        case_types=[TestCaseType.UNIT, TestCaseType.EDGE],
        constraints={'min_value': 1, 'max_value': 100},
        problem_id='summary-demo'
    )
    
    generator = SimpleTestGenerator(config)
    summary = generator.get_generation_summary()
    
    print("Generation Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print()

def main():
    """Run all demonstrations."""
    print("Test Generator Framework Demonstration\n")
    
    demo_basic_generation()
    demo_deterministic_generation()
    demo_constraints()
    demo_multiple_case_types()
    demo_edge_cases()
    demo_constraints_validation()
    demo_random_utilities()
    demo_generation_summary()
    
    print("Demo completed!")

if __name__ == "__main__":
    main()