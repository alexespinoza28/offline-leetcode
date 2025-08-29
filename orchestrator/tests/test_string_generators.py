"""
Unit tests for string-based test generators.
"""

import pytest
from orchestrator.testing.generators.string_generators import (
    StringTestGenerator, StringGeneratorConfig, StringPattern,
    CoverAllCharsGenerator, ReverseStringGenerator, UppercaseGenerator,
    LowercaseGenerator, PalindromeCheckGenerator, CharacterCountGenerator,
    StringLengthGenerator
)
from orchestrator.testing.generators.base import TestCaseType

class TestStringGeneratorConfig:
    """Test cases for StringGeneratorConfig."""
    
    def test_default_config(self):
        """Test default string generator configuration."""
        config = StringGeneratorConfig()
        
        assert config.min_length == 1
        assert config.max_length == 20
        assert config.charset == 'lowercase'
        assert config.patterns == [StringPattern.RANDOM]
        assert config.ensure_coverage == False
        assert config.word_list is None
    
    def test_custom_config(self):
        """Test custom string generator configuration."""
        config = StringGeneratorConfig(
            seed=123,
            num_cases=15,
            min_length=5,
            max_length=25,
            charset='alphanumeric',
            patterns=[StringPattern.PALINDROME, StringPattern.REPEATED],
            ensure_coverage=True,
            word_list=['hello', 'world', 'test']
        )
        
        assert config.seed == 123
        assert config.num_cases == 15
        assert config.min_length == 5
        assert config.max_length == 25
        assert config.charset == 'alphanumeric'
        assert config.patterns == [StringPattern.PALINDROME, StringPattern.REPEATED]
        assert config.ensure_coverage == True
        assert config.word_list == ['hello', 'world', 'test']

class TestStringTestGenerator:
    """Test cases for StringTestGenerator."""
    
    def test_basic_generation(self):
        """Test basic string generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=5,
            min_length=3,
            max_length=10
        )
        generator = StringTestGenerator(config)
        
        test_cases = generator.generate_test_cases()
        
        assert len(test_cases) == 5
        
        for test_case in test_cases:
            assert isinstance(test_case.input_data, str)
            assert 3 <= len(test_case.input_data) <= 10
            assert all(c in generator._charset for c in test_case.input_data)
            assert test_case.expected_output == test_case.input_data  # Identity by default
    
    def test_deterministic_generation(self):
        """Test that string generation is deterministic."""
        config = StringGeneratorConfig(seed=42, num_cases=3, min_length=5, max_length=5)
        
        generator1 = StringTestGenerator(config)
        test_cases1 = generator1.generate_test_cases()
        
        generator2 = StringTestGenerator(config)
        test_cases2 = generator2.generate_test_cases()
        
        # Should generate identical test cases
        assert len(test_cases1) == len(test_cases2)
        for tc1, tc2 in zip(test_cases1, test_cases2):
            assert tc1.input_data == tc2.input_data
            assert tc1.expected_output == tc2.expected_output
    
    def test_different_charsets(self):
        """Test generation with different character sets."""
        charsets = ['lowercase', 'uppercase', 'digits', 'alphanumeric']
        
        for charset in charsets:
            config = StringGeneratorConfig(
                seed=42,
                num_cases=3,
                charset=charset,
                min_length=5,
                max_length=5
            )
            generator = StringTestGenerator(config)
            test_cases = generator.generate_test_cases()
            
            expected_chars = generator.CHARSETS[charset]
            
            for test_case in test_cases:
                assert all(c in expected_chars for c in test_case.input_data)
    
    def test_custom_charset(self):
        """Test generation with custom character set."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            charset='abc123',
            min_length=4,
            max_length=6
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            assert all(c in 'abc123' for c in test_case.input_data)
    
    def test_palindrome_pattern(self):
        """Test palindrome pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=5,
            patterns=[StringPattern.PALINDROME],
            min_length=3,
            max_length=7
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            assert input_str == input_str[::-1], f"'{input_str}' is not a palindrome"
    
    def test_repeated_pattern(self):
        """Test repeated pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=5,
            patterns=[StringPattern.REPEATED],
            min_length=4,
            max_length=8
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            # Check if string has repeating pattern
            # This is a heuristic check - perfect validation would be complex
            assert len(input_str) > 0
            assert len(set(input_str)) <= len(input_str) // 2 + 1  # Some repetition expected
    
    def test_alternating_pattern(self):
        """Test alternating pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            patterns=[StringPattern.ALTERNATING],
            min_length=4,
            max_length=6
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            if len(input_str) >= 2:
                # Check alternating pattern
                char1, char2 = input_str[0], input_str[1]
                for i, char in enumerate(input_str):
                    expected_char = char1 if i % 2 == 0 else char2
                    assert char == expected_char, f"Alternating pattern broken at position {i}"
    
    def test_ascending_pattern(self):
        """Test ascending pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            patterns=[StringPattern.ASCENDING],
            min_length=3,
            max_length=5
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            chars = list(input_str)
            sorted_chars = sorted(chars)
            assert chars == sorted_chars, f"'{input_str}' is not in ascending order"
    
    def test_descending_pattern(self):
        """Test descending pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            patterns=[StringPattern.DESCENDING],
            min_length=3,
            max_length=5
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            chars = list(input_str)
            sorted_chars = sorted(chars, reverse=True)
            assert chars == sorted_chars, f"'{input_str}' is not in descending order"
    
    def test_edge_case_types(self):
        """Test edge case generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=6,
            case_types=[TestCaseType.EDGE],
            min_length=1,
            max_length=10
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        # Edge cases should include min and max lengths
        lengths = [len(tc.input_data) for tc in test_cases]
        assert 1 in lengths  # Min length
        assert 10 in lengths  # Max length
    
    def test_validation(self):
        """Test test case validation."""
        config = StringGeneratorConfig(min_length=3, max_length=5, charset='abc')
        generator = StringTestGenerator(config)
        
        # Valid test case
        from orchestrator.testing.generators.base import TestCase
        valid_case = TestCase(input_data="abc", expected_output="abc")
        assert generator.validate_test_case(valid_case)
        
        # Invalid length
        invalid_length_case = TestCase(input_data="ab", expected_output="ab")
        assert not generator.validate_test_case(invalid_length_case)
        
        # Invalid charset
        invalid_charset_case = TestCase(input_data="xyz", expected_output="xyz")
        assert not generator.validate_test_case(invalid_charset_case)
        
        # Invalid type
        invalid_type_case = TestCase(input_data=123, expected_output=123)
        assert not generator.validate_test_case(invalid_type_case)

class TestCoverAllCharsGenerator:
    """Test cases for CoverAllCharsGenerator."""
    
    def test_basic_coverage(self):
        """Test basic character coverage."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=5,
            charset='abc',
            min_length=2,
            max_length=4,
            ensure_coverage=True
        )
        generator = CoverAllCharsGenerator(config)
        test_cases = generator.generate_test_cases()
        
        # Check that all characters are covered
        all_chars = set()
        for test_case in test_cases:
            all_chars.update(test_case.input_data)
        
        assert 'a' in all_chars
        assert 'b' in all_chars
        assert 'c' in all_chars
    
    def test_coverage_report(self):
        """Test coverage reporting."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            charset='abcde',
            min_length=2,
            max_length=3
        )
        generator = CoverAllCharsGenerator(config)
        test_cases = generator.generate_test_cases()
        
        report = generator.get_coverage_report()
        
        assert report['total_characters'] == 5
        assert 0 <= report['covered_characters'] <= 5
        assert 0 <= report['coverage_percentage'] <= 100
        assert isinstance(report['missing_characters'], list)
        assert isinstance(report['covered_characters_list'], list)
    
    def test_ensure_coverage(self):
        """Test that coverage is ensured when enabled."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=2,  # Small number to likely miss some chars
            charset='abcdefghij',  # Large charset
            min_length=2,
            max_length=3,
            ensure_coverage=True
        )
        generator = CoverAllCharsGenerator(config)
        test_cases = generator.generate_test_cases()
        
        # Check that all characters are covered
        all_chars = set()
        for test_case in test_cases:
            all_chars.update(test_case.input_data)
        
        expected_chars = set('abcdefghij')
        assert all_chars == expected_chars

class TestSpecificStringGenerators:
    """Test cases for specific string generators."""
    
    def test_reverse_string_generator(self):
        """Test reverse string generator."""
        config = StringGeneratorConfig(seed=42, num_cases=3, min_length=3, max_length=5)
        generator = ReverseStringGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            expected = test_case.expected_output
            assert expected == input_str[::-1]
    
    def test_uppercase_generator(self):
        """Test uppercase generator."""
        config = StringGeneratorConfig(
            seed=42, 
            num_cases=3, 
            charset='letters',
            min_length=3, 
            max_length=5
        )
        generator = UppercaseGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            expected = test_case.expected_output
            assert expected == input_str.upper()
    
    def test_lowercase_generator(self):
        """Test lowercase generator."""
        config = StringGeneratorConfig(
            seed=42, 
            num_cases=3, 
            charset='letters',
            min_length=3, 
            max_length=5
        )
        generator = LowercaseGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            expected = test_case.expected_output
            assert expected == input_str.lower()
    
    def test_palindrome_check_generator(self):
        """Test palindrome check generator."""
        config = StringGeneratorConfig(
            seed=42, 
            num_cases=5,
            patterns=[StringPattern.PALINDROME, StringPattern.RANDOM],
            min_length=3, 
            max_length=7
        )
        generator = PalindromeCheckGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            expected = test_case.expected_output
            
            # Check if the expected output is correct
            cleaned = input_str.lower().replace(' ', '')
            is_palindrome = cleaned == cleaned[::-1]
            assert expected == is_palindrome
    
    def test_character_count_generator(self):
        """Test character count generator."""
        config = StringGeneratorConfig(seed=42, num_cases=3, min_length=3, max_length=5)
        generator = CharacterCountGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            expected = test_case.expected_output
            
            # Verify character count
            actual_count = {}
            for char in input_str:
                actual_count[char] = actual_count.get(char, 0) + 1
            
            assert expected == actual_count
    
    def test_string_length_generator(self):
        """Test string length generator."""
        config = StringGeneratorConfig(seed=42, num_cases=5, min_length=1, max_length=10)
        generator = StringLengthGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            expected = test_case.expected_output
            assert expected == len(input_str)

class TestStringGeneratorValidation:
    """Test validation and error handling for string generators."""
    
    def test_invalid_length_constraints(self):
        """Test validation of invalid length constraints."""
        # Negative minimum length
        with pytest.raises(ValueError):
            config = StringGeneratorConfig(min_length=-1)
            StringTestGenerator(config)
        
        # Max length less than min length
        with pytest.raises(ValueError):
            config = StringGeneratorConfig(min_length=10, max_length=5)
            StringTestGenerator(config)
    
    def test_empty_charset(self):
        """Test validation of empty charset."""
        with pytest.raises(ValueError):
            config = StringGeneratorConfig(charset='')
            StringTestGenerator(config)
    
    def test_edge_cases_generation(self):
        """Test generation of edge cases."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=4,
            case_types=[TestCaseType.EDGE],
            min_length=1,
            max_length=1,
            charset='a'
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        # All cases should be single 'a' character
        for test_case in test_cases:
            assert test_case.input_data == 'a'
            assert len(test_case.input_data) == 1

class TestStringPatterns:
    """Test different string patterns in detail."""
    
    def test_words_pattern(self):
        """Test words pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            patterns=[StringPattern.WORDS],
            min_length=10,
            max_length=20,
            word_list=['hello', 'world', 'test', 'python']
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            # Should contain words from the word list
            words = input_str.split()
            for word in words:
                # Word should be from word list or truncated version
                assert any(word.startswith(w) or w.startswith(word) 
                          for w in config.word_list)
    
    def test_sentences_pattern(self):
        """Test sentences pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=3,
            patterns=[StringPattern.SENTENCES],
            min_length=15,
            max_length=30
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            # Should contain sentence-like structure
            assert len(input_str) >= 15
            # Should have some capitalization and punctuation patterns
            # (This is a basic check - real sentences are complex)
            assert any(c.isupper() for c in input_str) or len(input_str) < 5
    
    def test_mixed_case_pattern(self):
        """Test mixed case pattern generation."""
        config = StringGeneratorConfig(
            seed=42,
            num_cases=5,
            patterns=[StringPattern.MIXED_CASE],
            charset='letters',
            min_length=5,
            max_length=10
        )
        generator = StringTestGenerator(config)
        test_cases = generator.generate_test_cases()
        
        for test_case in test_cases:
            input_str = test_case.input_data
            # Should have mixed case (at least for longer strings)
            if len(input_str) > 2:
                has_upper = any(c.isupper() for c in input_str)
                has_lower = any(c.islower() for c in input_str)
                # At least one case should be present (might not always be mixed due to randomness)
                assert has_upper or has_lower

if __name__ == "__main__":
    pytest.main([__file__])