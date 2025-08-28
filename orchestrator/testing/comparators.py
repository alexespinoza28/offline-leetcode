"""
Output comparison system for test case validation.

This module provides various comparators for different types of problems,
including exact text matching, numeric comparison with tolerance, and
custom comparison modes.
"""

import re
import json
import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass

class ComparisonResult(Enum):
    """Result of output comparison."""
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    ERROR = "ERROR"

@dataclass
class ComparisonDetails:
    """Detailed comparison result information."""
    result: ComparisonResult
    message: str = ""
    diff: Optional[str] = None
    expected_parsed: Optional[Any] = None
    actual_parsed: Optional[Any] = None
    similarity_score: float = 0.0

class OutputComparator(ABC):
    """Abstract base class for output comparators."""
    
    @abstractmethod
    def compare(self, expected: str, actual: str) -> ComparisonDetails:
        """Compare expected and actual output."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this comparator."""
        pass

class TextExactComparator(OutputComparator):
    """Exact text comparison with whitespace normalization."""
    
    def __init__(self, 
                 normalize_whitespace: bool = True,
                 ignore_trailing_whitespace: bool = True,
                 case_sensitive: bool = True):
        self.normalize_whitespace = normalize_whitespace
        self.ignore_trailing_whitespace = ignore_trailing_whitespace
        self.case_sensitive = case_sensitive
    
    def compare(self, expected: str, actual: str) -> ComparisonDetails:
        """Compare text with optional normalization."""
        try:
            # Normalize inputs
            exp_normalized = self._normalize_text(expected)
            act_normalized = self._normalize_text(actual)
            
            if exp_normalized == act_normalized:
                return ComparisonDetails(
                    result=ComparisonResult.MATCH,
                    message="Output matches exactly",
                    similarity_score=1.0
                )
            else:
                diff = self._generate_diff(expected, actual)
                similarity = self._calculate_similarity(exp_normalized, act_normalized)
                
                return ComparisonDetails(
                    result=ComparisonResult.MISMATCH,
                    message=f"Text mismatch (similarity: {similarity:.1%})",
                    diff=diff,
                    similarity_score=similarity
                )
                
        except Exception as e:
            return ComparisonDetails(
                result=ComparisonResult.ERROR,
                message=f"Comparison error: {str(e)}"
            )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text according to configuration."""
        if not self.case_sensitive:
            text = text.lower()
        
        if self.ignore_trailing_whitespace:
            text = text.rstrip()
        
        if self.normalize_whitespace:
            # Normalize multiple whitespace to single space
            text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def _generate_diff(self, expected: str, actual: str) -> str:
        """Generate a detailed diff between expected and actual."""
        exp_lines = expected.split('\n')
        act_lines = actual.split('\n')
        
        diff_lines = []
        max_lines = max(len(exp_lines), len(act_lines))
        
        for i in range(max_lines):
            exp_line = exp_lines[i] if i < len(exp_lines) else ""
            act_line = act_lines[i] if i < len(act_lines) else ""
            
            if exp_line != act_line:
                diff_lines.append(f"Line {i+1}:")
                diff_lines.append(f"  Expected: {repr(exp_line)}")
                diff_lines.append(f"  Actual:   {repr(act_line)}")
                
                # Show character-level diff for short lines
                if len(exp_line) < 100 and len(act_line) < 100:
                    char_diff = self._character_diff(exp_line, act_line)
                    if char_diff:
                        diff_lines.append(f"  Diff:     {char_diff}")
        
        return '\n'.join(diff_lines) if diff_lines else "No differences found"
    
    def _character_diff(self, expected: str, actual: str) -> str:
        """Generate character-level diff visualization."""
        result = []
        i = j = 0
        
        while i < len(expected) or j < len(actual):
            if i < len(expected) and j < len(actual):
                if expected[i] == actual[j]:
                    result.append(expected[i])
                    i += 1
                    j += 1
                else:
                    result.append(f"[{expected[i]}→{actual[j]}]")
                    i += 1
                    j += 1
            elif i < len(expected):
                result.append(f"[-{expected[i]}]")
                i += 1
            else:
                result.append(f"[+{actual[j]}]")
                j += 1
        
        return ''.join(result)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity score between two texts."""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # Simple Levenshtein-based similarity
        max_len = max(len(text1), len(text2))
        distance = self._levenshtein_distance(text1, text2)
        return max(0.0, 1.0 - distance / max_len)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_name(self) -> str:
        return "TextExact"

class NumericComparator(OutputComparator):
    """Numeric comparison with configurable epsilon tolerance."""
    
    def __init__(self, 
                 epsilon: float = 1e-9,
                 relative_tolerance: float = 1e-6,
                 allow_scientific_notation: bool = True):
        self.epsilon = epsilon
        self.relative_tolerance = relative_tolerance
        self.allow_scientific_notation = allow_scientific_notation
    
    def compare(self, expected: str, actual: str) -> ComparisonDetails:
        """Compare numeric outputs with tolerance."""
        try:
            exp_numbers = self._extract_numbers(expected)
            act_numbers = self._extract_numbers(actual)
            
            if len(exp_numbers) != len(act_numbers):
                return ComparisonDetails(
                    result=ComparisonResult.MISMATCH,
                    message=f"Different number of numeric values: expected {len(exp_numbers)}, got {len(act_numbers)}",
                    expected_parsed=exp_numbers,
                    actual_parsed=act_numbers
                )
            
            mismatches = []
            total_error = 0.0
            
            for i, (exp_val, act_val) in enumerate(zip(exp_numbers, act_numbers)):
                if not self._numbers_equal(exp_val, act_val):
                    error = abs(exp_val - act_val)
                    relative_error = error / max(abs(exp_val), abs(act_val), 1e-10)
                    mismatches.append({
                        'index': i,
                        'expected': exp_val,
                        'actual': act_val,
                        'absolute_error': error,
                        'relative_error': relative_error
                    })
                    total_error += error
            
            if not mismatches:
                return ComparisonDetails(
                    result=ComparisonResult.MATCH,
                    message="All numeric values match within tolerance",
                    expected_parsed=exp_numbers,
                    actual_parsed=act_numbers,
                    similarity_score=1.0
                )
            else:
                avg_error = total_error / len(exp_numbers)
                similarity = max(0.0, 1.0 - min(1.0, avg_error))
                
                diff = self._format_numeric_diff(mismatches)
                return ComparisonDetails(
                    result=ComparisonResult.MISMATCH,
                    message=f"{len(mismatches)} numeric mismatches (avg error: {avg_error:.2e})",
                    diff=diff,
                    expected_parsed=exp_numbers,
                    actual_parsed=act_numbers,
                    similarity_score=similarity
                )
                
        except Exception as e:
            return ComparisonDetails(
                result=ComparisonResult.ERROR,
                message=f"Numeric comparison error: {str(e)}"
            )
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text."""
        # Pattern for scientific notation and regular numbers
        if self.allow_scientific_notation:
            pattern = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
        else:
            pattern = r'[-+]?(?:\d+\.?\d*|\.\d+)'
        
        matches = re.findall(pattern, text)
        return [float(match) for match in matches]
    
    def _numbers_equal(self, a: float, b: float) -> bool:
        """Check if two numbers are equal within tolerance."""
        if math.isnan(a) and math.isnan(b):
            return True
        if math.isinf(a) and math.isinf(b):
            return math.copysign(1, a) == math.copysign(1, b)
        
        abs_diff = abs(a - b)
        
        # Absolute tolerance check
        if abs_diff <= self.epsilon:
            return True
        
        # Relative tolerance check
        max_val = max(abs(a), abs(b))
        if max_val > 0 and abs_diff / max_val <= self.relative_tolerance:
            return True
        
        return False
    
    def _format_numeric_diff(self, mismatches: List[Dict]) -> str:
        """Format numeric differences for display."""
        lines = []
        for mismatch in mismatches:
            lines.append(f"Value {mismatch['index']}:")
            lines.append(f"  Expected: {mismatch['expected']}")
            lines.append(f"  Actual:   {mismatch['actual']}")
            lines.append(f"  Abs Error: {mismatch['absolute_error']:.2e}")
            lines.append(f"  Rel Error: {mismatch['relative_error']:.2%}")
        
        return '\n'.join(lines)
    
    def get_name(self) -> str:
        return "Numeric"

class JsonComparator(OutputComparator):
    """JSON structure comparison with flexible ordering."""
    
    def __init__(self, 
                 ignore_order: bool = True,
                 ignore_extra_fields: bool = False,
                 numeric_tolerance: float = 1e-9):
        self.ignore_order = ignore_order
        self.ignore_extra_fields = ignore_extra_fields
        self.numeric_tolerance = numeric_tolerance
    
    def compare(self, expected: str, actual: str) -> ComparisonDetails:
        """Compare JSON structures."""
        try:
            exp_json = json.loads(expected.strip())
            act_json = json.loads(actual.strip())
            
            differences = []
            self._compare_json_recursive(exp_json, act_json, "", differences)
            
            if not differences:
                return ComparisonDetails(
                    result=ComparisonResult.MATCH,
                    message="JSON structures match",
                    expected_parsed=exp_json,
                    actual_parsed=act_json,
                    similarity_score=1.0
                )
            else:
                diff = '\n'.join(differences)
                similarity = max(0.0, 1.0 - min(1.0, len(differences) / 10))
                
                return ComparisonDetails(
                    result=ComparisonResult.MISMATCH,
                    message=f"{len(differences)} JSON differences found",
                    diff=diff,
                    expected_parsed=exp_json,
                    actual_parsed=act_json,
                    similarity_score=similarity
                )
                
        except json.JSONDecodeError as e:
            return ComparisonDetails(
                result=ComparisonResult.ERROR,
                message=f"JSON parsing error: {str(e)}"
            )
        except Exception as e:
            return ComparisonDetails(
                result=ComparisonResult.ERROR,
                message=f"JSON comparison error: {str(e)}"
            )
    
    def _compare_json_recursive(self, expected: Any, actual: Any, path: str, differences: List[str]):
        """Recursively compare JSON structures."""
        if type(expected) != type(actual):
            differences.append(f"{path}: Type mismatch - expected {type(expected).__name__}, got {type(actual).__name__}")
            return
        
        if isinstance(expected, dict):
            self._compare_dicts(expected, actual, path, differences)
        elif isinstance(expected, list):
            self._compare_lists(expected, actual, path, differences)
        elif isinstance(expected, (int, float)):
            if not self._numbers_equal(float(expected), float(actual)):
                differences.append(f"{path}: Numeric mismatch - expected {expected}, got {actual}")
        else:
            if expected != actual:
                differences.append(f"{path}: Value mismatch - expected {repr(expected)}, got {repr(actual)}")
    
    def _compare_dicts(self, expected: dict, actual: dict, path: str, differences: List[str]):
        """Compare dictionary structures."""
        if not self.ignore_extra_fields:
            extra_keys = set(actual.keys()) - set(expected.keys())
            if extra_keys:
                differences.append(f"{path}: Extra keys in actual: {sorted(extra_keys)}")
        
        missing_keys = set(expected.keys()) - set(actual.keys())
        if missing_keys:
            differences.append(f"{path}: Missing keys in actual: {sorted(missing_keys)}")
        
        for key in expected:
            if key in actual:
                new_path = f"{path}.{key}" if path else key
                self._compare_json_recursive(expected[key], actual[key], new_path, differences)
    
    def _compare_lists(self, expected: list, actual: list, path: str, differences: List[str]):
        """Compare list structures."""
        if len(expected) != len(actual):
            differences.append(f"{path}: Length mismatch - expected {len(expected)}, got {len(actual)}")
            return
        
        if self.ignore_order:
            # Try to match elements regardless of order
            self._compare_lists_unordered(expected, actual, path, differences)
        else:
            # Compare in order
            for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                new_path = f"{path}[{i}]"
                self._compare_json_recursive(exp_item, act_item, new_path, differences)
    
    def _compare_lists_unordered(self, expected: list, actual: list, path: str, differences: List[str]):
        """Compare lists ignoring order."""
        # This is a simplified approach - for complex cases, we'd need better matching
        exp_sorted = sorted(expected, key=lambda x: json.dumps(x, sort_keys=True))
        act_sorted = sorted(actual, key=lambda x: json.dumps(x, sort_keys=True))
        
        for i, (exp_item, act_item) in enumerate(zip(exp_sorted, act_sorted)):
            new_path = f"{path}[{i}] (sorted)"
            self._compare_json_recursive(exp_item, act_item, new_path, differences)
    
    def _numbers_equal(self, a: float, b: float) -> bool:
        """Check numeric equality with tolerance."""
        return abs(a - b) <= self.numeric_tolerance
    
    def get_name(self) -> str:
        return "JSON"

class ArrayComparator(OutputComparator):
    """Array/list comparison with flexible formatting."""
    
    def __init__(self, 
                 ignore_order: bool = False,
                 ignore_brackets: bool = True,
                 separator_pattern: str = r'[,\s]+'):
        self.ignore_order = ignore_order
        self.ignore_brackets = ignore_brackets
        self.separator_pattern = separator_pattern
    
    def compare(self, expected: str, actual: str) -> ComparisonDetails:
        """Compare array-like outputs."""
        try:
            exp_array = self._parse_array(expected)
            act_array = self._parse_array(actual)
            
            if self.ignore_order:
                exp_array = sorted(exp_array)
                act_array = sorted(act_array)
            
            if exp_array == act_array:
                return ComparisonDetails(
                    result=ComparisonResult.MATCH,
                    message="Arrays match",
                    expected_parsed=exp_array,
                    actual_parsed=act_array,
                    similarity_score=1.0
                )
            else:
                diff = self._generate_array_diff(exp_array, act_array)
                similarity = self._calculate_array_similarity(exp_array, act_array)
                
                return ComparisonDetails(
                    result=ComparisonResult.MISMATCH,
                    message=f"Array mismatch (similarity: {similarity:.1%})",
                    diff=diff,
                    expected_parsed=exp_array,
                    actual_parsed=act_array,
                    similarity_score=similarity
                )
                
        except Exception as e:
            return ComparisonDetails(
                result=ComparisonResult.ERROR,
                message=f"Array comparison error: {str(e)}"
            )
    
    def _parse_array(self, text: str) -> List[str]:
        """Parse array from text."""
        text = text.strip()
        
        if self.ignore_brackets:
            # Remove common bracket types
            text = re.sub(r'^[\[\(]', '', text)
            text = re.sub(r'[\]\)]$', '', text)
        
        # Split by separator pattern
        if not text:
            return []
        
        elements = re.split(self.separator_pattern, text)
        return [elem.strip().strip('"\'') for elem in elements if elem.strip()]
    
    def _generate_array_diff(self, expected: List[str], actual: List[str]) -> str:
        """Generate array difference visualization."""
        lines = []
        lines.append(f"Expected: {expected}")
        lines.append(f"Actual:   {actual}")
        
        if len(expected) != len(actual):
            lines.append(f"Length difference: expected {len(expected)}, got {len(actual)}")
        
        # Show element differences
        max_len = max(len(expected), len(actual))
        for i in range(max_len):
            exp_elem = expected[i] if i < len(expected) else "<missing>"
            act_elem = actual[i] if i < len(actual) else "<extra>"
            
            if exp_elem != act_elem:
                lines.append(f"  [{i}]: {repr(exp_elem)} → {repr(act_elem)}")
        
        return '\n'.join(lines)
    
    def _calculate_array_similarity(self, arr1: List[str], arr2: List[str]) -> float:
        """Calculate similarity between arrays."""
        if not arr1 and not arr2:
            return 1.0
        if not arr1 or not arr2:
            return 0.0
        
        # Jaccard similarity
        set1 = set(arr1)
        set2 = set(arr2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_name(self) -> str:
        return "Array"

class ComparatorFactory:
    """Factory for creating appropriate comparators based on problem type."""
    
    @staticmethod
    def create_comparator(comparison_type: str, **kwargs) -> OutputComparator:
        """Create a comparator based on type."""
        comparators = {
            'exact': TextExactComparator,
            'text': TextExactComparator,
            'numeric': NumericComparator,
            'json': JsonComparator,
            'array': ArrayComparator,
        }
        
        comparator_class = comparators.get(comparison_type.lower())
        if not comparator_class:
            raise ValueError(f"Unknown comparator type: {comparison_type}")
        
        return comparator_class(**kwargs)
    
    @staticmethod
    def auto_detect_comparator(expected: str, actual: str) -> OutputComparator:
        """Auto-detect the best comparator for the given outputs."""
        exp_stripped = expected.strip()
        act_stripped = actual.strip()
        
        # Check if it looks like an array first (before JSON, since arrays are valid JSON)
        if ((exp_stripped.startswith('[') and exp_stripped.endswith(']')) or \
           (exp_stripped.startswith('(') and exp_stripped.endswith(')'))) and \
           ((act_stripped.startswith('[') and act_stripped.endswith(']')) or \
           (act_stripped.startswith('(') and act_stripped.endswith(')'))):
            # Check if it's a simple array (not complex JSON)
            try:
                exp_parsed = json.loads(exp_stripped)
                act_parsed = json.loads(act_stripped)
                # If it's a simple list of primitives, use ArrayComparator
                if isinstance(exp_parsed, list) and isinstance(act_parsed, list):
                    if all(isinstance(x, (str, int, float, bool, type(None))) for x in exp_parsed):
                        return ArrayComparator()
            except:
                # If JSON parsing fails, still try array comparator
                return ArrayComparator()
        
        # Try JSON for complex structures
        try:
            json.loads(exp_stripped)
            json.loads(act_stripped)
            return JsonComparator()
        except:
            pass
        
        # Check if it's primarily numeric
        numeric_pattern = r'^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?(?:\s*,?\s*[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)*$'
        if re.match(numeric_pattern, exp_stripped) and re.match(numeric_pattern, act_stripped):
            return NumericComparator()
        
        # Default to text comparison
        return TextExactComparator()