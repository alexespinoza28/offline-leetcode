"""
Constraint system for test case generation.

This module provides various constraint types that can be used to control
and validate test case generation parameters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Union, Set
import re

class Constraint(ABC):
    """Abstract base class for all constraints."""
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """
        Validate that a value satisfies this constraint.
        
        Args:
            value: Value to validate
            
        Returns:
            True if value satisfies constraint, False otherwise
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of this constraint."""
        pass

@dataclass
class RangeConstraint(Constraint):
    """Constraint for numeric ranges."""
    
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    inclusive_min: bool = True
    inclusive_max: bool = True
    
    def validate(self, value: Any) -> bool:
        """Validate that value is within the specified range."""
        if not isinstance(value, (int, float)):
            return False
        
        if self.min_value is not None:
            if self.inclusive_min:
                if value < self.min_value:
                    return False
            else:
                if value <= self.min_value:
                    return False
        
        if self.max_value is not None:
            if self.inclusive_max:
                if value > self.max_value:
                    return False
            else:
                if value >= self.max_value:
                    return False
        
        return True
    
    def get_description(self) -> str:
        """Get description of the range constraint."""
        parts = []
        
        if self.min_value is not None:
            op = ">=" if self.inclusive_min else ">"
            parts.append(f"value {op} {self.min_value}")
        
        if self.max_value is not None:
            op = "<=" if self.inclusive_max else "<"
            parts.append(f"value {op} {self.max_value}")
        
        return " and ".join(parts) if parts else "no range constraint"
    
    def get_valid_range(self) -> tuple:
        """Get the valid range as a tuple (min, max)."""
        return (self.min_value, self.max_value)

@dataclass
class LengthConstraint(Constraint):
    """Constraint for sequence lengths."""
    
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    exact_length: Optional[int] = None
    
    def __post_init__(self):
        """Validate constraint parameters."""
        if self.exact_length is not None:
            if self.min_length is not None or self.max_length is not None:
                raise ValueError("Cannot specify exact_length with min_length or max_length")
        
        if self.min_length is not None and self.max_length is not None:
            if self.min_length > self.max_length:
                raise ValueError("min_length cannot be greater than max_length")
    
    def validate(self, value: Any) -> bool:
        """Validate that value has acceptable length."""
        try:
            length = len(value)
        except TypeError:
            return False
        
        if self.exact_length is not None:
            return length == self.exact_length
        
        if self.min_length is not None and length < self.min_length:
            return False
        
        if self.max_length is not None and length > self.max_length:
            return False
        
        return True
    
    def get_description(self) -> str:
        """Get description of the length constraint."""
        if self.exact_length is not None:
            return f"length = {self.exact_length}"
        
        parts = []
        if self.min_length is not None:
            parts.append(f"length >= {self.min_length}")
        if self.max_length is not None:
            parts.append(f"length <= {self.max_length}")
        
        return " and ".join(parts) if parts else "no length constraint"
    
    def get_valid_lengths(self) -> List[int]:
        """Get list of valid lengths."""
        if self.exact_length is not None:
            return [self.exact_length]
        
        min_len = self.min_length or 0
        max_len = self.max_length or 100  # Default reasonable maximum
        
        return list(range(min_len, max_len + 1))

@dataclass
class CharsetConstraint(Constraint):
    """Constraint for character sets in strings."""
    
    allowed_chars: Optional[Set[str]] = None
    forbidden_chars: Optional[Set[str]] = None
    charset_name: Optional[str] = None
    
    # Predefined character sets
    CHARSETS = {
        'lowercase': set('abcdefghijklmnopqrstuvwxyz'),
        'uppercase': set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'letters': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'digits': set('0123456789'),
        'alphanumeric': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        'ascii_printable': set(''.join(chr(i) for i in range(32, 127))),
        'ascii_letters': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    }
    
    def __post_init__(self):
        """Initialize charset from name if provided."""
        if self.charset_name:
            if self.charset_name not in self.CHARSETS:
                raise ValueError(f"Unknown charset: {self.charset_name}")
            
            if self.allowed_chars is None:
                self.allowed_chars = self.CHARSETS[self.charset_name].copy()
            else:
                # Intersect with named charset
                self.allowed_chars &= self.CHARSETS[self.charset_name]
    
    def validate(self, value: Any) -> bool:
        """Validate that string contains only allowed characters."""
        if not isinstance(value, str):
            return False
        
        char_set = set(value)
        
        # Check forbidden characters
        if self.forbidden_chars:
            if char_set & self.forbidden_chars:
                return False
        
        # Check allowed characters
        if self.allowed_chars:
            if not char_set.issubset(self.allowed_chars):
                return False
        
        return True
    
    def get_description(self) -> str:
        """Get description of the charset constraint."""
        parts = []
        
        if self.charset_name:
            parts.append(f"charset: {self.charset_name}")
        
        if self.allowed_chars:
            if len(self.allowed_chars) <= 10:
                chars_str = ''.join(sorted(self.allowed_chars))
                parts.append(f"allowed: '{chars_str}'")
            else:
                parts.append(f"allowed: {len(self.allowed_chars)} characters")
        
        if self.forbidden_chars:
            if len(self.forbidden_chars) <= 10:
                chars_str = ''.join(sorted(self.forbidden_chars))
                parts.append(f"forbidden: '{chars_str}'")
            else:
                parts.append(f"forbidden: {len(self.forbidden_chars)} characters")
        
        return ", ".join(parts) if parts else "no charset constraint"
    
    def get_allowed_chars(self) -> Set[str]:
        """Get the set of allowed characters."""
        if self.allowed_chars:
            result = self.allowed_chars.copy()
            if self.forbidden_chars:
                result -= self.forbidden_chars
            return result
        
        # If no allowed chars specified, use all printable ASCII minus forbidden
        result = self.CHARSETS['ascii_printable'].copy()
        if self.forbidden_chars:
            result -= self.forbidden_chars
        
        return result

@dataclass
class PatternConstraint(Constraint):
    """Constraint for regex pattern matching."""
    
    pattern: str
    flags: int = 0
    
    def __post_init__(self):
        """Compile the regex pattern."""
        try:
            self._regex = re.compile(self.pattern, self.flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{self.pattern}': {e}")
    
    def validate(self, value: Any) -> bool:
        """Validate that value matches the regex pattern."""
        if not isinstance(value, str):
            return False
        
        return bool(self._regex.match(value))
    
    def get_description(self) -> str:
        """Get description of the pattern constraint."""
        return f"matches pattern: {self.pattern}"

@dataclass
class UniqueConstraint(Constraint):
    """Constraint ensuring all elements in a sequence are unique."""
    
    def validate(self, value: Any) -> bool:
        """Validate that all elements in sequence are unique."""
        try:
            # Convert to list to handle various sequence types
            items = list(value)
            return len(items) == len(set(items))
        except (TypeError, ValueError):
            return False
    
    def get_description(self) -> str:
        """Get description of the unique constraint."""
        return "all elements must be unique"

@dataclass
class SortedConstraint(Constraint):
    """Constraint ensuring sequence is sorted."""
    
    ascending: bool = True
    strict: bool = False  # If True, requires strictly increasing/decreasing
    
    def validate(self, value: Any) -> bool:
        """Validate that sequence is sorted."""
        try:
            items = list(value)
            if len(items) <= 1:
                return True
            
            if self.ascending:
                if self.strict:
                    return all(items[i] < items[i + 1] for i in range(len(items) - 1))
                else:
                    return all(items[i] <= items[i + 1] for i in range(len(items) - 1))
            else:
                if self.strict:
                    return all(items[i] > items[i + 1] for i in range(len(items) - 1))
                else:
                    return all(items[i] >= items[i + 1] for i in range(len(items) - 1))
        
        except (TypeError, ValueError):
            return False
    
    def get_description(self) -> str:
        """Get description of the sorted constraint."""
        direction = "ascending" if self.ascending else "descending"
        strictness = "strictly " if self.strict else ""
        return f"{strictness}sorted {direction}"

class ConstraintValidator:
    """Utility class for validating values against multiple constraints."""
    
    def __init__(self, constraints: List[Constraint]):
        """
        Initialize validator with list of constraints.
        
        Args:
            constraints: List of constraints to validate against
        """
        self.constraints = constraints
    
    def validate(self, value: Any) -> bool:
        """
        Validate value against all constraints.
        
        Args:
            value: Value to validate
            
        Returns:
            True if value satisfies all constraints, False otherwise
        """
        return all(constraint.validate(value) for constraint in self.constraints)
    
    def get_violations(self, value: Any) -> List[str]:
        """
        Get list of constraint violations for a value.
        
        Args:
            value: Value to check
            
        Returns:
            List of descriptions of violated constraints
        """
        violations = []
        for constraint in self.constraints:
            if not constraint.validate(value):
                violations.append(constraint.get_description())
        
        return violations
    
    def get_description(self) -> str:
        """Get description of all constraints."""
        if not self.constraints:
            return "no constraints"
        
        descriptions = [constraint.get_description() for constraint in self.constraints]
        return " and ".join(descriptions)