"""
Unit tests for the test generator framework.
"""

import pytest
from orchestrator.testing.generators.base import (
    TestGenerator, GeneratorConfig, TestCase, TestCaseType, SimpleTestGenerator
)
from orchestrator.testing.generators.constraints import (
    RangeConstraint, LengthConstraint, CharsetConstraint, PatternConstraint,
    UniqueConstraint, SortedConstraint, ConstraintValidator
)

class TestGeneratorConfig:
    """Test cases for GeneratorConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = GeneratorConfig()
        
        assert config.seed == 42
        assert config.num_cases == 10
        assert config.case_types == [TestCaseType.UNIT]
        assert config.constraints == {}
        assert config.problem_id is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = GeneratorConfig(
            seed=123,
            num_cases=20,
            case_types=[TestCaseType.EDGE, TestCaseType.STRESS],
            constraints={'max_value': 100},
            problem_id='test-problem'
        )
        
        assert config.seed == 123
        assert config.num_cases == 20
        assert config.case_types == [TestCaseType.EDGE, TestCaseType.STRESS]
        assert config.constraints == {'max_value': 100}
        assert config.problem_id == 'test-problem'
    
    def test_deterministic_seed(self):
        """Test deterministic seed generation."""
        config = GeneratorConfig(seed=42, problem_id='test-problem')
        
        # Same inputs should produce same seed
        seed1 = config.get_deterministic_seed(0)
        seed2 = config.get_deterministic_seed(0)
        assert seed1 == seed2
        
        # Different case indices should produce different seeds
        seed3 = config.get_deterministic_seed(1)
        assert seed1 != seed3
        
        # Different problem IDs should produce different seeds
        config2 = GeneratorConfig(seed=42, problem_id='other-problem')
        seed4 = config2.get_deterministic_seed(0)
        assert seed1 != seed4

class TestTestCase:
    """Test cases for TestCase."""
    
    def test_basic_test_case(self):
        """Test basic test case creation."""
        test_case = TestCase(
            input_data=[1, 2, 3],
            expected_output=6
        )
        
        assert test_case.input_data == [1, 2, 3]
        assert test_case.expected_output == 6
        assert test_case.case_type == TestCaseType.UNIT
        assert test_case.description is None
        assert test_case.metadata == {}
    
    def test_test_case_with_metadata(self):
        """Test test case with metadata."""
        test_case = TestCase(
            input_data="hello",
            expected_output="HELLO",
            case_type=TestCaseType.EDGE,
            description="Uppercase conversion",
            metadata={'complexity': 'low', 'category': 'string'}
        )
        
        assert test_case.case_type == TestCaseType.EDGE
        assert test_case.description == "Uppercase conversion"
        assert test_case.metadata['complexity'] == 'low'
        assert test_case.metadata['category'] == 'string'
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        test_case = TestCase(
            input_data=42,
            expected_output=84,
            case_type=TestCaseType.STRESS,
            description="Double the number",
            metadata={'seed': 123}
        )
        
        result = test_case.to_dict()
        
        expected = {
            'input': 42,
            'expected_output': 84,
            'type': 'stress',
            'description': 'Double the number',
            'metadata': {'seed': 123}
        }
        
        assert result == expected

class TestSimpleTestGenerator:
    """Test cases for SimpleTestGenerator."""
    
    def test_basic_generation(self):
        """Test basic test case generation."""
        config = GeneratorConfig(num_cases=5, seed=42)
        generator = SimpleTestGenerator(config)
        
        test_cases = generator.generate_test_cases()
        
        assert len(test_cases) == 5
        
        for test_case in test_cases:
            assert isinstance(test_case.input_data, int)
            assert isinstance(test_case.expected_output, int)
            assert test_case.expected_output == test_case.input_data * 2
            assert test_case.case_type == TestCaseType.UNIT
            assert 'seed' in test_case.metadata
            assert 'case_index' in test_case.metadata
    
    def test_deterministic_generation(self):
        """Test that generation is deterministic."""
        config = GeneratorConfig(num_cases=3, seed=42)
        
        generator1 = SimpleTestGenerator(config)
        test_cases1 = generator1.generate_test_cases()
        
        generator2 = SimpleTestGenerator(config)
        test_cases2 = generator2.generate_test_cases()
        
        # Should generate identical test cases
        assert len(test_cases1) == len(test_cases2)
        for tc1, tc2 in zip(test_cases1, test_cases2):
            assert tc1.input_data == tc2.input_data
            assert tc1.expected_output == tc2.expected_output
            assert tc1.metadata['seed'] == tc2.metadata['seed']
    
    def test_constraints(self):
        """Test generation with constraints."""
        config = GeneratorConfig(
            num_cases=10,
            seed=42,
            constraints={'min_value': 50, 'max_value': 60}
        )
        generator = SimpleTestGenerator(config)
        
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            assert 50 <= test_case.input_data <= 60
    
    def test_multiple_case_types(self):
        """Test generation with multiple case types."""
        config = GeneratorConfig(
            num_cases=6,
            seed=42,
            case_types=[TestCaseType.UNIT, TestCaseType.EDGE]
        )
        generator = SimpleTestGenerator(config)
        
        test_cases = generator.generate_test_cases()
        
        assert len(test_cases) == 6
        
        # Should have both unit and edge cases
        unit_cases = [tc for tc in test_cases if tc.case_type == TestCaseType.UNIT]
        edge_cases = [tc for tc in test_cases if tc.case_type == TestCaseType.EDGE]
        
        assert len(unit_cases) == 3
        assert len(edge_cases) == 3
    
    def test_edge_cases(self):
        """Test edge case generation."""
        config = GeneratorConfig(
            num_cases=2,
            seed=42,
            case_types=[TestCaseType.EDGE]
        )
        generator = SimpleTestGenerator(config)
        
        test_cases = generator.generate_test_cases()
        edge_cases = generator.generate_edge_cases()
        
        # All generated cases should be edge cases
        for test_case in test_cases:
            assert test_case.case_type == TestCaseType.EDGE
        
        # Should have predefined edge cases
        assert len(edge_cases) == 2
        assert any(tc.input_data == 0 for tc in edge_cases)
        assert any(tc.input_data == -1 for tc in edge_cases)
    
    def test_validation(self):
        """Test test case validation."""
        config = GeneratorConfig()
        generator = SimpleTestGenerator(config)
        
        # Valid test case
        valid_case = TestCase(input_data=5, expected_output=10)
        assert generator.validate_test_case(valid_case)
        
        # Invalid test case (wrong output)
        invalid_case = TestCase(input_data=5, expected_output=15)
        assert not generator.validate_test_case(invalid_case)
        
        # Invalid test case (wrong type)
        invalid_type_case = TestCase(input_data="5", expected_output=10)
        assert not generator.validate_test_case(invalid_type_case)
    
    def test_generation_summary(self):
        """Test generation summary."""
        config = GeneratorConfig(
            seed=123,
            num_cases=5,
            case_types=[TestCaseType.UNIT, TestCaseType.EDGE],
            constraints={'max_value': 100},
            problem_id='test-problem'
        )
        generator = SimpleTestGenerator(config)
        
        summary = generator.get_generation_summary()
        
        assert summary['generator_type'] == 'SimpleTestGenerator'
        assert summary['seed'] == 123
        assert summary['num_cases'] == 5
        assert summary['case_types'] == ['unit', 'edge']
        assert summary['constraints'] == {'max_value': 100}
        assert summary['problem_id'] == 'test-problem'
    
    def test_random_utilities(self):
        """Test random utility methods."""
        config = GeneratorConfig(seed=42)
        generator = SimpleTestGenerator(config)
        
        # Test random int
        val = generator.generate_random_int(1, 10)
        assert 1 <= val <= 10
        assert isinstance(val, int)
        
        # Test random float
        val = generator.generate_random_float(1.0, 10.0)
        assert 1.0 <= val <= 10.0
        assert isinstance(val, float)
        
        # Test random choice
        choices = ['a', 'b', 'c']
        val = generator.generate_random_choice(choices)
        assert val in choices
        
        # Test random sample
        population = [1, 2, 3, 4, 5]
        sample = generator.generate_random_sample(population, 3)
        assert len(sample) == 3
        assert all(item in population for item in sample)
        assert len(set(sample)) == 3  # No duplicates
        
        # Test random string
        string = generator.generate_random_string(5)
        assert len(string) == 5
        assert all(c.islower() and c.isalpha() for c in string)
        
        # Test random string with custom charset
        string = generator.generate_random_string(3, '123')
        assert len(string) == 3
        assert all(c in '123' for c in string)
        
        # Test shuffle
        items = [1, 2, 3, 4, 5]
        shuffled = generator.shuffle_list(items)
        assert len(shuffled) == len(items)
        assert set(shuffled) == set(items)
        # Original list should be unchanged
        assert items == [1, 2, 3, 4, 5]

class TestConstraints:
    """Test cases for constraint classes."""
    
    def test_range_constraint(self):
        """Test RangeConstraint."""
        # Basic range
        constraint = RangeConstraint(min_value=1, max_value=10)
        
        assert constraint.validate(5)
        assert constraint.validate(1)  # Inclusive by default
        assert constraint.validate(10)  # Inclusive by default
        assert not constraint.validate(0)
        assert not constraint.validate(11)
        assert not constraint.validate("5")  # Wrong type
        
        # Exclusive range
        constraint = RangeConstraint(
            min_value=1, max_value=10,
            inclusive_min=False, inclusive_max=False
        )
        
        assert constraint.validate(5)
        assert not constraint.validate(1)
        assert not constraint.validate(10)
        
        # Only minimum
        constraint = RangeConstraint(min_value=5)
        assert constraint.validate(5)
        assert constraint.validate(100)
        assert not constraint.validate(4)
        
        # Only maximum
        constraint = RangeConstraint(max_value=5)
        assert constraint.validate(5)
        assert constraint.validate(-100)
        assert not constraint.validate(6)
    
    def test_length_constraint(self):
        """Test LengthConstraint."""
        # Exact length
        constraint = LengthConstraint(exact_length=5)
        
        assert constraint.validate("hello")
        assert constraint.validate([1, 2, 3, 4, 5])
        assert not constraint.validate("hi")
        assert not constraint.validate([1, 2, 3])
        
        # Range length
        constraint = LengthConstraint(min_length=2, max_length=5)
        
        assert constraint.validate("hi")
        assert constraint.validate("hello")
        assert not constraint.validate("h")
        assert not constraint.validate("toolong")
        
        # Invalid configuration
        with pytest.raises(ValueError):
            LengthConstraint(exact_length=5, min_length=3)
        
        with pytest.raises(ValueError):
            LengthConstraint(min_length=10, max_length=5)
    
    def test_charset_constraint(self):
        """Test CharsetConstraint."""
        # Allowed characters
        constraint = CharsetConstraint(allowed_chars=set('abc'))
        
        assert constraint.validate("abc")
        assert constraint.validate("a")
        assert constraint.validate("")
        assert not constraint.validate("abcd")
        assert not constraint.validate("xyz")
        
        # Forbidden characters
        constraint = CharsetConstraint(forbidden_chars=set('xyz'))
        
        assert constraint.validate("abc")
        assert not constraint.validate("axyz")
        
        # Named charset
        constraint = CharsetConstraint(charset_name='digits')
        
        assert constraint.validate("123")
        assert not constraint.validate("abc")
        assert not constraint.validate("12a")
        
        # Invalid charset name
        with pytest.raises(ValueError):
            CharsetConstraint(charset_name='invalid')
    
    def test_pattern_constraint(self):
        """Test PatternConstraint."""
        # Email pattern
        constraint = PatternConstraint(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        assert constraint.validate("test@example.com")
        assert constraint.validate("user.name+tag@domain.co.uk")
        assert not constraint.validate("invalid-email")
        assert not constraint.validate("@example.com")
        
        # Invalid pattern
        with pytest.raises(ValueError):
            PatternConstraint(r'[invalid')
    
    def test_unique_constraint(self):
        """Test UniqueConstraint."""
        constraint = UniqueConstraint()
        
        assert constraint.validate([1, 2, 3])
        assert constraint.validate("abc")
        assert constraint.validate([])
        assert not constraint.validate([1, 2, 2])
        assert not constraint.validate("aab")
    
    def test_sorted_constraint(self):
        """Test SortedConstraint."""
        # Ascending (default)
        constraint = SortedConstraint()
        
        assert constraint.validate([1, 2, 3])
        assert constraint.validate([1, 2, 2])  # Non-strict
        assert constraint.validate([])
        assert constraint.validate([1])
        assert not constraint.validate([3, 2, 1])
        
        # Strictly ascending
        constraint = SortedConstraint(strict=True)
        
        assert constraint.validate([1, 2, 3])
        assert not constraint.validate([1, 2, 2])
        
        # Descending
        constraint = SortedConstraint(ascending=False)
        
        assert constraint.validate([3, 2, 1])
        assert constraint.validate([3, 2, 2])
        assert not constraint.validate([1, 2, 3])
        
        # Strictly descending
        constraint = SortedConstraint(ascending=False, strict=True)
        
        assert constraint.validate([3, 2, 1])
        assert not constraint.validate([3, 2, 2])
    
    def test_constraint_validator(self):
        """Test ConstraintValidator."""
        # Test with constraints that can both apply to the same value
        constraints = [
            LengthConstraint(min_length=2, max_length=5),
            CharsetConstraint(allowed_chars=set('abc'))
        ]
        validator = ConstraintValidator(constraints)
        
        # Valid value
        assert validator.validate("abc")
        
        # Invalid values
        assert not validator.validate("a")  # Length violation
        assert not validator.validate("abcdef")  # Length violation  
        assert not validator.validate("xyz")  # Charset violation
        assert not validator.validate("abx")  # Charset violation
        
        # Get violations
        violations = validator.get_violations("a")
        assert len(violations) == 1
        assert "length >= 2" in violations[0]
        
        violations = validator.get_violations("xyz")
        assert len(violations) == 1
        assert "allowed" in violations[0]
        
        # Multiple violations
        violations = validator.get_violations("x")
        assert len(violations) == 2

class TestGeneratorValidation:
    """Test generator validation and error handling."""
    
    def test_invalid_config(self):
        """Test validation of invalid configurations."""
        # Negative number of cases
        with pytest.raises(ValueError):
            config = GeneratorConfig(num_cases=-1)
            SimpleTestGenerator(config)
        
        # Zero cases
        with pytest.raises(ValueError):
            config = GeneratorConfig(num_cases=0)
            SimpleTestGenerator(config)
        
        # Empty case types
        with pytest.raises(ValueError):
            config = GeneratorConfig(case_types=[])
            SimpleTestGenerator(config)

if __name__ == "__main__":
    pytest.main([__file__])