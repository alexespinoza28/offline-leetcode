"""
String-based test generators for string manipulation problems.

This module provides specialized generators for creating test cases
involving strings with various constraints and patterns.
"""

import random
from typing import List, Set, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .base import TestGenerator, GeneratorConfig, TestCase, TestCaseType
from .constraints import (
    LengthConstraint, CharsetConstraint, PatternConstraint, 
    UniqueConstraint, ConstraintValidator
)

class StringPattern(Enum):
    """Common string patterns for generation."""
    RANDOM = "random"
    PALINDROME = "palindrome"
    REPEATED = "repeated"
    ALTERNATING = "alternating"
    ASCENDING = "ascending"
    DESCENDING = "descending"
    MIXED_CASE = "mixed_case"
    WORDS = "words"
    SENTENCES = "sentences"

@dataclass
class StringGeneratorConfig(GeneratorConfig):
    """Extended configuration for string generators."""
    min_length: int = 1
    max_length: int = 20
    charset: str = 'lowercase'
    patterns: List[StringPattern] = None
    ensure_coverage: bool = False
    word_list: Optional[List[str]] = None
    
    def __post_init__(self):
        """Initialize default patterns if not provided."""
        if self.patterns is None:
            self.patterns = [StringPattern.RANDOM]

class StringTestGenerator(TestGenerator):
    """Base class for string-based test generators."""
    
    # Predefined character sets
    CHARSETS = {
        'lowercase': 'abcdefghijklmnopqrstuvwxyz',
        'uppercase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'letters': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'digits': '0123456789',
        'alphanumeric': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        'ascii_printable': ''.join(chr(i) for i in range(32, 127)),
        'vowels': 'aeiouAEIOU',
        'consonants': 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ',
        'special': '!@#$%^&*()_+-=[]{}|;:,.<>?',
        'whitespace': ' \t\n\r',
    }
    
    def __init__(self, config: StringGeneratorConfig):
        """Initialize string test generator."""
        if not isinstance(config, StringGeneratorConfig):
            # Convert regular config to string config
            config = StringGeneratorConfig(
                seed=config.seed,
                num_cases=config.num_cases,
                case_types=config.case_types,
                constraints=config.constraints,
                problem_id=config.problem_id
            )
        
        # Set string_config before calling super().__init__() so it's available during validation
        self.string_config = config
        self._charset = self._get_charset()
        self._length_constraint = LengthConstraint(
            min_length=config.min_length,
            max_length=config.max_length
        )
        
        super().__init__(config)
    
    def _get_charset(self) -> str:
        """Get the character set for generation."""
        charset_name = self.string_config.charset
        if charset_name in self.CHARSETS:
            return self.CHARSETS[charset_name]
        else:
            # Assume it's a custom charset
            return charset_name
    
    def _validate_constraints(self):
        """Validate string generator constraints."""
        if self.string_config.min_length < 0:
            raise ValueError("Minimum length cannot be negative")
        
        if self.string_config.max_length < self.string_config.min_length:
            raise ValueError("Maximum length cannot be less than minimum length")
        
        if not self._charset:
            raise ValueError("Character set cannot be empty")
    
    def _generate_single_case(self, case_type: TestCaseType, case_index: int) -> TestCase:
        """Generate a single string test case."""
        # Choose pattern based on case type
        if case_type == TestCaseType.EDGE:
            pattern = self._choose_edge_pattern()
        else:
            pattern = self.generate_random_choice(self.string_config.patterns)
        
        # Generate string based on pattern
        input_string = self._generate_string_by_pattern(pattern, case_type)
        
        # Generate expected output (override in subclasses)
        expected_output = self._compute_expected_output(input_string)
        
        return TestCase(
            input_data=input_string,
            expected_output=expected_output,
            description=f"{pattern.value} string: '{input_string}'"
        )
    
    def _choose_edge_pattern(self) -> StringPattern:
        """Choose a pattern suitable for edge cases."""
        edge_patterns = [
            StringPattern.PALINDROME,
            StringPattern.REPEATED,
            StringPattern.ALTERNATING
        ]
        return self.generate_random_choice(edge_patterns)
    
    def _generate_string_by_pattern(self, pattern: StringPattern, case_type: TestCaseType) -> str:
        """Generate a string following the specified pattern."""
        length = self._choose_length(case_type)
        
        if pattern == StringPattern.RANDOM:
            return self._generate_random_string(length)
        elif pattern == StringPattern.PALINDROME:
            return self._generate_palindrome(length)
        elif pattern == StringPattern.REPEATED:
            return self._generate_repeated_string(length)
        elif pattern == StringPattern.ALTERNATING:
            return self._generate_alternating_string(length)
        elif pattern == StringPattern.ASCENDING:
            return self._generate_ascending_string(length)
        elif pattern == StringPattern.DESCENDING:
            return self._generate_descending_string(length)
        elif pattern == StringPattern.MIXED_CASE:
            return self._generate_mixed_case_string(length)
        elif pattern == StringPattern.WORDS:
            return self._generate_words_string(length)
        elif pattern == StringPattern.SENTENCES:
            return self._generate_sentences_string(length)
        else:
            return self._generate_random_string(length)
    
    def _choose_length(self, case_type: TestCaseType) -> int:
        """Choose appropriate length based on case type."""
        min_len = self.string_config.min_length
        max_len = self.string_config.max_length
        
        if case_type == TestCaseType.EDGE:
            # Choose edge lengths - ensure we get both min and max
            edge_lengths = [min_len, max_len]
            if min_len < max_len:
                # Add middle length for variety
                edge_lengths.append((min_len + max_len) // 2)
            # Duplicate min and max to increase their probability
            edge_lengths.extend([min_len, max_len])
            return self.generate_random_choice(edge_lengths)
        elif case_type == TestCaseType.STRESS:
            # Prefer longer strings for stress testing
            return self.generate_random_int(max(min_len, max_len - 5), max_len)
        else:
            # Normal distribution
            return self.generate_random_int(min_len, max_len)
    
    def _generate_random_string(self, length: int) -> str:
        """Generate a random string of specified length."""
        return ''.join(self.generate_random_choice(self._charset) for _ in range(length))
    
    def _generate_palindrome(self, length: int) -> str:
        """Generate a palindromic string."""
        if length == 0:
            return ""
        
        half_length = length // 2
        half = self._generate_random_string(half_length)
        
        if length % 2 == 0:
            return half + half[::-1]
        else:
            middle = self.generate_random_choice(self._charset)
            return half + middle + half[::-1]
    
    def _generate_repeated_string(self, length: int) -> str:
        """Generate a string with repeated patterns."""
        if length == 0:
            return ""
        
        # Choose pattern length (1 to length//2)
        pattern_length = self.generate_random_int(1, max(1, length // 2))
        pattern = self._generate_random_string(pattern_length)
        
        # Repeat pattern to fill length
        result = (pattern * ((length // pattern_length) + 1))[:length]
        return result
    
    def _generate_alternating_string(self, length: int) -> str:
        """Generate a string with alternating characters."""
        if length == 0:
            return ""
        
        # Choose two characters to alternate
        char1 = self.generate_random_choice(self._charset)
        char2 = self.generate_random_choice(self._charset)
        
        result = []
        for i in range(length):
            result.append(char1 if i % 2 == 0 else char2)
        
        return ''.join(result)
    
    def _generate_ascending_string(self, length: int) -> str:
        """Generate a string with characters in ascending order."""
        if length == 0:
            return ""
        
        # Sort charset and choose consecutive characters
        sorted_chars = sorted(self._charset)
        if len(sorted_chars) < length:
            # If not enough unique chars, allow repetition
            chars = [self.generate_random_choice(sorted_chars) for _ in range(length)]
            chars.sort()
        else:
            # Choose random starting position
            start_idx = self.generate_random_int(0, len(sorted_chars) - length)
            chars = sorted_chars[start_idx:start_idx + length]
        
        return ''.join(chars)
    
    def _generate_descending_string(self, length: int) -> str:
        """Generate a string with characters in descending order."""
        ascending = self._generate_ascending_string(length)
        return ascending[::-1]
    
    def _generate_mixed_case_string(self, length: int) -> str:
        """Generate a string with mixed case (if applicable)."""
        if 'letters' not in self.string_config.charset and 'alphanumeric' not in self.string_config.charset:
            return self._generate_random_string(length)
        
        result = []
        for _ in range(length):
            char = self.generate_random_choice(self._charset)
            if char.isalpha():
                # Randomly choose case
                char = char.upper() if self._random.random() < 0.5 else char.lower()
            result.append(char)
        
        return ''.join(result)
    
    def _generate_words_string(self, length: int) -> str:
        """Generate a string that looks like words."""
        if self.string_config.word_list:
            words = self.string_config.word_list
        else:
            # Generate random words
            words = []
            remaining = length
            while remaining > 0:
                word_len = min(self.generate_random_int(2, 8), remaining)
                word = self._generate_random_string(word_len)
                words.append(word)
                remaining -= word_len
                if remaining > 0:
                    remaining -= 1  # Account for space
        
        result = ' '.join(words)
        return result[:length]  # Truncate to exact length
    
    def _generate_sentences_string(self, length: int) -> str:
        """Generate a string that looks like sentences."""
        if length < 3:
            return self._generate_random_string(length)
        
        result = []
        remaining = length
        
        while remaining > 0:
            # Generate sentence of random length
            sentence_len = min(self.generate_random_int(5, 20), remaining - 1)
            sentence = self._generate_words_string(sentence_len)
            
            # Capitalize first letter and add period
            if sentence:
                sentence = sentence[0].upper() + sentence[1:] + '.'
                result.append(sentence)
                remaining -= len(sentence)
                
                if remaining > 0:
                    result.append(' ')
                    remaining -= 1
            else:
                break
        
        return ''.join(result)[:length]
    
    def _compute_expected_output(self, input_string: str) -> str:
        """Compute expected output for input string. Override in subclasses."""
        # Default: return the input string (identity function)
        return input_string
    
    def _validate_test_case_constraints(self, test_case: TestCase) -> bool:
        """Validate string test case constraints."""
        if not isinstance(test_case.input_data, str):
            return False
        
        # Check length constraint
        if not self._length_constraint.validate(test_case.input_data):
            return False
        
        # Check charset constraint
        charset_constraint = CharsetConstraint(allowed_chars=set(self._charset))
        if not charset_constraint.validate(test_case.input_data):
            return False
        
        return True

class CoverAllCharsGenerator(StringTestGenerator):
    """Generator that ensures alphabet coverage in generated strings."""
    
    def __init__(self, config: StringGeneratorConfig):
        """Initialize cover all chars generator."""
        super().__init__(config)
        self._coverage_tracker = set()
    
    def generate_test_cases(self) -> List[TestCase]:
        """Generate test cases ensuring character coverage."""
        # Reset coverage tracker
        self._coverage_tracker = set()
        
        # Generate normal test cases
        test_cases = super().generate_test_cases()
        
        # Check coverage and add cases if needed
        missing_chars = set(self._charset) - self._coverage_tracker
        
        if missing_chars and self.string_config.ensure_coverage:
            # Generate additional cases to cover missing characters
            coverage_cases = self._generate_coverage_cases(missing_chars)
            test_cases.extend(coverage_cases)
        
        return test_cases
    
    def _generate_single_case(self, case_type: TestCaseType, case_index: int) -> TestCase:
        """Generate a single case and track character coverage."""
        test_case = super()._generate_single_case(case_type, case_index)
        
        # Track characters used
        self._coverage_tracker.update(test_case.input_data)
        
        return test_case
    
    def _generate_coverage_cases(self, missing_chars: Set[str]) -> List[TestCase]:
        """Generate additional test cases to cover missing characters."""
        coverage_cases = []
        
        # Group missing characters into strings
        missing_list = list(missing_chars)
        
        while missing_list:
            # Take up to max_length characters
            chunk_size = min(len(missing_list), self.string_config.max_length)
            chunk = missing_list[:chunk_size]
            missing_list = missing_list[chunk_size:]
            
            # Create string with missing characters
            coverage_string = ''.join(chunk)
            
            # Pad with random characters if needed
            if len(coverage_string) < self.string_config.min_length:
                padding_needed = self.string_config.min_length - len(coverage_string)
                padding = self._generate_random_string(padding_needed)
                coverage_string += padding
            
            # Shuffle the string
            coverage_list = list(coverage_string)
            self._random.shuffle(coverage_list)
            coverage_string = ''.join(coverage_list)
            
            expected_output = self._compute_expected_output(coverage_string)
            
            test_case = TestCase(
                input_data=coverage_string,
                expected_output=expected_output,
                case_type=TestCaseType.UNIT,
                description=f"Coverage case: ensures chars {chunk}"
            )
            
            coverage_cases.append(test_case)
        
        return coverage_cases
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Get character coverage report."""
        total_chars = len(self._charset)
        covered_chars = len(self._coverage_tracker)
        missing_chars = set(self._charset) - self._coverage_tracker
        
        return {
            'total_characters': total_chars,
            'covered_characters': covered_chars,
            'coverage_percentage': (covered_chars / total_chars) * 100 if total_chars > 0 else 0,
            'missing_characters': sorted(missing_chars),
            'covered_characters_list': sorted(self._coverage_tracker)
        }

class ReverseStringGenerator(StringTestGenerator):
    """Generator for string reversal problems."""
    
    def _compute_expected_output(self, input_string: str) -> str:
        """Reverse the input string."""
        return input_string[::-1]

class UppercaseGenerator(StringTestGenerator):
    """Generator for string uppercase conversion problems."""
    
    def _compute_expected_output(self, input_string: str) -> str:
        """Convert input string to uppercase."""
        return input_string.upper()

class LowercaseGenerator(StringTestGenerator):
    """Generator for string lowercase conversion problems."""
    
    def _compute_expected_output(self, input_string: str) -> str:
        """Convert input string to lowercase."""
        return input_string.lower()

class PalindromeCheckGenerator(StringTestGenerator):
    """Generator for palindrome checking problems."""
    
    def __init__(self, config: StringGeneratorConfig):
        """Initialize palindrome check generator."""
        super().__init__(config)
        # Ensure we generate both palindromes and non-palindromes
        if StringPattern.PALINDROME not in config.patterns:
            config.patterns.append(StringPattern.PALINDROME)
    
    def _compute_expected_output(self, input_string: str) -> bool:
        """Check if input string is a palindrome."""
        cleaned = input_string.lower().replace(' ', '')
        return cleaned == cleaned[::-1]

class CharacterCountGenerator(StringTestGenerator):
    """Generator for character counting problems."""
    
    def _compute_expected_output(self, input_string: str) -> Dict[str, int]:
        """Count characters in the input string."""
        char_count = {}
        for char in input_string:
            char_count[char] = char_count.get(char, 0) + 1
        return char_count

class StringLengthGenerator(StringTestGenerator):
    """Generator for string length problems."""
    
    def _compute_expected_output(self, input_string: str) -> int:
        """Return the length of the input string."""
        return len(input_string)