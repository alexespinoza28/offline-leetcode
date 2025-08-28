import pytest
import json
from orchestrator.testing.comparators import (
    TextExactComparator,
    NumericComparator,
    JsonComparator,
    ArrayComparator,
    ComparatorFactory,
    ComparisonResult
)

class TestTextExactComparator:
    """Test cases for TextExactComparator."""
    
    def test_exact_match(self):
        """Test exact text matching."""
        comparator = TextExactComparator()
        result = comparator.compare("Hello World", "Hello World")
        
        assert result.result == ComparisonResult.MATCH
        assert result.similarity_score == 1.0
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        comparator = TextExactComparator(normalize_whitespace=True)
        result = comparator.compare("Hello   World\n", "Hello World")
        
        assert result.result == ComparisonResult.MATCH
        assert result.similarity_score == 1.0
    
    def test_case_sensitivity(self):
        """Test case sensitivity options."""
        # Case sensitive (default)
        comparator = TextExactComparator(case_sensitive=True)
        result = comparator.compare("Hello", "hello")
        assert result.result == ComparisonResult.MISMATCH
        
        # Case insensitive
        comparator = TextExactComparator(case_sensitive=False)
        result = comparator.compare("Hello", "hello")
        assert result.result == ComparisonResult.MATCH
    
    def test_diff_generation(self):
        """Test diff generation for mismatches."""
        comparator = TextExactComparator()
        result = comparator.compare("Hello World", "Hello Universe")
        
        assert result.result == ComparisonResult.MISMATCH
        assert result.diff is not None
        assert "World" in result.diff
        assert "Universe" in result.diff
    
    def test_multiline_comparison(self):
        """Test multiline text comparison."""
        expected = "Line 1\nLine 2\nLine 3"
        actual = "Line 1\nLine 2 Modified\nLine 3"
        
        comparator = TextExactComparator()
        result = comparator.compare(expected, actual)
        
        assert result.result == ComparisonResult.MISMATCH
        assert "Line 2" in result.diff
        assert result.similarity_score > 0.5  # Should be partially similar

class TestNumericComparator:
    """Test cases for NumericComparator."""
    
    def test_exact_numeric_match(self):
        """Test exact numeric matching."""
        comparator = NumericComparator()
        result = comparator.compare("42", "42")
        
        assert result.result == ComparisonResult.MATCH
        assert result.similarity_score == 1.0
    
    def test_floating_point_tolerance(self):
        """Test floating point tolerance."""
        comparator = NumericComparator(epsilon=1e-6)
        result = comparator.compare("3.14159", "3.141591")
        
        assert result.result == ComparisonResult.MATCH
    
    def test_scientific_notation(self):
        """Test scientific notation support."""
        comparator = NumericComparator()
        result = comparator.compare("1e-6", "0.000001")
        
        assert result.result == ComparisonResult.MATCH
    
    def test_multiple_numbers(self):
        """Test multiple numbers in output."""
        comparator = NumericComparator()
        result = comparator.compare("1.5 2.7 3.14", "1.5 2.7 3.14")
        
        assert result.result == ComparisonResult.MATCH
        assert len(result.expected_parsed) == 3
    
    def test_numeric_mismatch(self):
        """Test numeric mismatch detection."""
        comparator = NumericComparator(epsilon=1e-9)
        result = comparator.compare("3.14159", "2.71828")
        
        assert result.result == ComparisonResult.MISMATCH
        assert result.diff is not None
        assert "absolute_error" in result.diff.lower()
    
    def test_different_number_count(self):
        """Test different number of values."""
        comparator = NumericComparator()
        result = comparator.compare("1 2 3", "1 2")
        
        assert result.result == ComparisonResult.MISMATCH
        assert "different number" in result.message.lower()
    
    def test_special_values(self):
        """Test special numeric values (inf, nan)."""
        comparator = NumericComparator()
        
        # Infinity
        result = comparator.compare("inf", "inf")
        assert result.result == ComparisonResult.MATCH
        
        # NaN (should match NaN)
        result = comparator.compare("nan", "nan")
        assert result.result == ComparisonResult.MATCH

class TestJsonComparator:
    """Test cases for JsonComparator."""
    
    def test_simple_json_match(self):
        """Test simple JSON matching."""
        comparator = JsonComparator()
        json_str = '{"name": "John", "age": 30}'
        result = comparator.compare(json_str, json_str)
        
        assert result.result == ComparisonResult.MATCH
        assert result.similarity_score == 1.0
    
    def test_json_order_independence(self):
        """Test JSON key order independence."""
        comparator = JsonComparator(ignore_order=True)
        json1 = '{"name": "John", "age": 30}'
        json2 = '{"age": 30, "name": "John"}'
        result = comparator.compare(json1, json2)
        
        assert result.result == ComparisonResult.MATCH
    
    def test_json_array_comparison(self):
        """Test JSON array comparison."""
        comparator = JsonComparator(ignore_order=True)
        json1 = '{"items": [1, 2, 3]}'
        json2 = '{"items": [3, 1, 2]}'
        result = comparator.compare(json1, json2)
        
        assert result.result == ComparisonResult.MATCH
    
    def test_nested_json_comparison(self):
        """Test nested JSON structure comparison."""
        comparator = JsonComparator()
        json1 = '{"user": {"name": "John", "details": {"age": 30}}}'
        json2 = '{"user": {"name": "John", "details": {"age": 31}}}'
        result = comparator.compare(json1, json2)
        
        assert result.result == ComparisonResult.MISMATCH
        assert "age" in result.diff
    
    def test_json_numeric_tolerance(self):
        """Test numeric tolerance in JSON."""
        comparator = JsonComparator(numeric_tolerance=1e-6)
        json1 = '{"value": 3.14159}'
        json2 = '{"value": 3.141591}'
        result = comparator.compare(json1, json2)
        
        assert result.result == ComparisonResult.MATCH
    
    def test_invalid_json(self):
        """Test invalid JSON handling."""
        comparator = JsonComparator()
        result = comparator.compare('{"invalid": json}', '{"valid": "json"}')
        
        assert result.result == ComparisonResult.ERROR
        assert "json parsing error" in result.message.lower()
    
    def test_extra_fields(self):
        """Test extra fields handling."""
        # Ignore extra fields
        comparator = JsonComparator(ignore_extra_fields=True)
        json1 = '{"name": "John"}'
        json2 = '{"name": "John", "age": 30}'
        result = comparator.compare(json1, json2)
        assert result.result == ComparisonResult.MATCH
        
        # Don't ignore extra fields
        comparator = JsonComparator(ignore_extra_fields=False)
        result = comparator.compare(json1, json2)
        assert result.result == ComparisonResult.MISMATCH

class TestArrayComparator:
    """Test cases for ArrayComparator."""
    
    def test_simple_array_match(self):
        """Test simple array matching."""
        comparator = ArrayComparator()
        result = comparator.compare("[1, 2, 3]", "[1, 2, 3]")
        
        assert result.result == ComparisonResult.MATCH
        assert result.similarity_score == 1.0
    
    def test_array_order_independence(self):
        """Test array order independence."""
        comparator = ArrayComparator(ignore_order=True)
        result = comparator.compare("[1, 2, 3]", "[3, 1, 2]")
        
        assert result.result == ComparisonResult.MATCH
    
    def test_different_brackets(self):
        """Test different bracket types."""
        comparator = ArrayComparator(ignore_brackets=True)
        result = comparator.compare("[1, 2, 3]", "(1, 2, 3)")
        
        assert result.result == ComparisonResult.MATCH
    
    def test_space_separated_arrays(self):
        """Test space-separated arrays."""
        comparator = ArrayComparator(separator_pattern=r'\s+')
        result = comparator.compare("1 2 3", "1 2 3")
        
        assert result.result == ComparisonResult.MATCH
    
    def test_array_mismatch(self):
        """Test array mismatch detection."""
        comparator = ArrayComparator()
        result = comparator.compare("[1, 2, 3]", "[1, 2, 4]")
        
        assert result.result == ComparisonResult.MISMATCH
        assert result.diff is not None
        assert "3" in result.diff and "4" in result.diff
    
    def test_different_lengths(self):
        """Test arrays with different lengths."""
        comparator = ArrayComparator()
        result = comparator.compare("[1, 2, 3]", "[1, 2]")
        
        assert result.result == ComparisonResult.MISMATCH
        assert "length difference" in result.diff.lower()
    
    def test_empty_arrays(self):
        """Test empty array handling."""
        comparator = ArrayComparator()
        result = comparator.compare("[]", "[]")
        
        assert result.result == ComparisonResult.MATCH
        
        result = comparator.compare("", "")
        assert result.result == ComparisonResult.MATCH

class TestComparatorFactory:
    """Test cases for ComparatorFactory."""
    
    def test_create_text_comparator(self):
        """Test creating text comparator."""
        comparator = ComparatorFactory.create_comparator('text')
        assert isinstance(comparator, TextExactComparator)
        assert comparator.get_name() == "TextExact"
    
    def test_create_numeric_comparator(self):
        """Test creating numeric comparator."""
        comparator = ComparatorFactory.create_comparator('numeric', epsilon=1e-6)
        assert isinstance(comparator, NumericComparator)
        assert comparator.epsilon == 1e-6
    
    def test_create_json_comparator(self):
        """Test creating JSON comparator."""
        comparator = ComparatorFactory.create_comparator('json')
        assert isinstance(comparator, JsonComparator)
    
    def test_create_array_comparator(self):
        """Test creating array comparator."""
        comparator = ComparatorFactory.create_comparator('array')
        assert isinstance(comparator, ArrayComparator)
    
    def test_invalid_comparator_type(self):
        """Test invalid comparator type."""
        with pytest.raises(ValueError):
            ComparatorFactory.create_comparator('invalid_type')
    
    def test_auto_detect_json(self):
        """Test auto-detection of JSON."""
        comparator = ComparatorFactory.auto_detect_comparator('{"key": "value"}', '{"key": "value"}')
        assert isinstance(comparator, JsonComparator)
    
    def test_auto_detect_array(self):
        """Test auto-detection of array."""
        comparator = ComparatorFactory.auto_detect_comparator('[1, 2, 3]', '[1, 2, 3]')
        assert isinstance(comparator, ArrayComparator)
    
    def test_auto_detect_numeric(self):
        """Test auto-detection of numeric."""
        comparator = ComparatorFactory.auto_detect_comparator('3.14159', '2.71828')
        assert isinstance(comparator, NumericComparator)
    
    def test_auto_detect_text(self):
        """Test auto-detection defaults to text."""
        comparator = ComparatorFactory.auto_detect_comparator('Hello World', 'Hello Universe')
        assert isinstance(comparator, TextExactComparator)

class TestIntegrationScenarios:
    """Integration test scenarios with real problem examples."""
    
    def test_two_sum_problem(self):
        """Test Two Sum problem output comparison."""
        # Array output
        comparator = ArrayComparator(ignore_order=False)
        result = comparator.compare("[0,1]", "[0,1]")
        assert result.result == ComparisonResult.MATCH
        
        result = comparator.compare("[0,1]", "[1,0]")
        assert result.result == ComparisonResult.MISMATCH
    
    def test_floating_point_problem(self):
        """Test floating point problem comparison."""
        comparator = NumericComparator(epsilon=1e-5)
        result = comparator.compare("3.14159", "3.14160")
        assert result.result == ComparisonResult.MATCH
        
        result = comparator.compare("3.14159", "3.15000")
        assert result.result == ComparisonResult.MISMATCH
    
    def test_string_problem(self):
        """Test string problem comparison."""
        comparator = TextExactComparator(normalize_whitespace=True)
        result = comparator.compare("abc", "abc")
        assert result.result == ComparisonResult.MATCH
        
        result = comparator.compare("abc\n", "abc")
        assert result.result == ComparisonResult.MATCH
    
    def test_complex_json_problem(self):
        """Test complex JSON structure comparison."""
        expected = '{"result": [{"id": 1, "value": 3.14}, {"id": 2, "value": 2.71}]}'
        actual = '{"result": [{"id": 1, "value": 3.140001}, {"id": 2, "value": 2.71}]}'
        
        comparator = JsonComparator(numeric_tolerance=1e-4)
        result = comparator.compare(expected, actual)
        assert result.result == ComparisonResult.MATCH

if __name__ == "__main__":
    pytest.main([__file__])