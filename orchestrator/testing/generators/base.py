"""
Base test generator framework with seeded random number generation.

This module provides the abstract base class for all test generators,
ensuring deterministic test case generation with proper constraint handling.
"""

import random
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum

class TestCaseType(Enum):
    """Types of test cases that can be generated."""
    SAMPLE = "sample"
    UNIT = "unit" 
    HIDDEN = "hidden"
    EDGE = "edge"
    STRESS = "stress"

@dataclass
class TestCase:
    """Represents a single test case with input and expected output."""
    input_data: Any
    expected_output: Any
    case_type: TestCaseType = TestCaseType.UNIT
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test case to dictionary format."""
        return {
            'input': self.input_data,
            'expected_output': self.expected_output,
            'type': self.case_type.value,
            'description': self.description,
            'metadata': self.metadata
        }

@dataclass
class GeneratorConfig:
    """Configuration for test case generation."""
    seed: int = 42
    num_cases: int = 10
    case_types: List[TestCaseType] = field(default_factory=lambda: [TestCaseType.UNIT])
    constraints: Dict[str, Any] = field(default_factory=dict)
    problem_id: Optional[str] = None
    
    def get_deterministic_seed(self, case_index: int) -> int:
        """Generate a deterministic seed for a specific test case."""
        # Create a deterministic seed based on base seed, problem_id, and case index
        seed_string = f"{self.seed}:{self.problem_id or 'default'}:{case_index}"
        hash_object = hashlib.md5(seed_string.encode())
        return int(hash_object.hexdigest()[:8], 16)

class TestGenerator(ABC):
    """Abstract base class for test case generators."""
    
    def __init__(self, config: GeneratorConfig):
        """
        Initialize the test generator.
        
        Args:
            config: Configuration for test generation
        """
        self.config = config
        self._random = random.Random()
        self._validate_config()
    
    def _validate_config(self):
        """Validate the generator configuration."""
        if self.config.num_cases <= 0:
            raise ValueError("Number of test cases must be positive")
        
        if not self.config.case_types:
            raise ValueError("At least one case type must be specified")
        
        # Allow subclasses to add additional validation
        self._validate_constraints()
    
    @abstractmethod
    def _validate_constraints(self):
        """Validate generator-specific constraints. Override in subclasses."""
        pass
    
    def generate_test_cases(self) -> List[TestCase]:
        """
        Generate all test cases according to the configuration.
        
        Returns:
            List of generated test cases
        """
        test_cases = []
        
        # Distribute cases across different types
        cases_per_type = self._distribute_cases_by_type()
        
        case_index = 0
        for case_type, count in cases_per_type.items():
            for i in range(count):
                # Set deterministic seed for this specific case
                seed = self.config.get_deterministic_seed(case_index)
                self._random.seed(seed)
                
                # Generate the test case
                test_case = self._generate_single_case(case_type, case_index)
                test_case.case_type = case_type
                test_case.metadata['seed'] = seed
                test_case.metadata['case_index'] = case_index
                
                test_cases.append(test_case)
                case_index += 1
        
        return test_cases
    
    def _distribute_cases_by_type(self) -> Dict[TestCaseType, int]:
        """Distribute the total number of cases across different types."""
        total_cases = self.config.num_cases
        case_types = self.config.case_types
        
        if len(case_types) == 1:
            return {case_types[0]: total_cases}
        
        # Default distribution strategy
        cases_per_type = {}
        base_count = total_cases // len(case_types)
        remainder = total_cases % len(case_types)
        
        for i, case_type in enumerate(case_types):
            count = base_count + (1 if i < remainder else 0)
            cases_per_type[case_type] = count
        
        return cases_per_type
    
    @abstractmethod
    def _generate_single_case(self, case_type: TestCaseType, case_index: int) -> TestCase:
        """
        Generate a single test case of the specified type.
        
        Args:
            case_type: Type of test case to generate
            case_index: Index of this case in the overall generation
            
        Returns:
            Generated test case
        """
        pass
    
    def generate_random_int(self, min_val: int, max_val: int) -> int:
        """Generate a random integer within the specified range."""
        return self._random.randint(min_val, max_val)
    
    def generate_random_float(self, min_val: float, max_val: float) -> float:
        """Generate a random float within the specified range."""
        return self._random.uniform(min_val, max_val)
    
    def generate_random_choice(self, choices: List[Any]) -> Any:
        """Choose a random element from the given list."""
        return self._random.choice(choices)
    
    def generate_random_sample(self, population: List[Any], k: int) -> List[Any]:
        """Generate a random sample of k elements from the population."""
        return self._random.sample(population, k)
    
    def generate_random_string(self, length: int, charset: str = None) -> str:
        """
        Generate a random string of specified length.
        
        Args:
            length: Length of the string to generate
            charset: Character set to use (default: lowercase letters)
            
        Returns:
            Random string
        """
        if charset is None:
            charset = 'abcdefghijklmnopqrstuvwxyz'
        
        return ''.join(self._random.choice(charset) for _ in range(length))
    
    def shuffle_list(self, items: List[Any]) -> List[Any]:
        """Shuffle a list in-place and return it."""
        items_copy = items.copy()
        self._random.shuffle(items_copy)
        return items_copy
    
    def get_constraint(self, key: str, default: Any = None) -> Any:
        """Get a constraint value from the configuration."""
        return self.config.constraints.get(key, default)
    
    def has_constraint(self, key: str) -> bool:
        """Check if a constraint exists in the configuration."""
        return key in self.config.constraints
    
    def validate_test_case(self, test_case: TestCase) -> bool:
        """
        Validate that a generated test case meets all constraints.
        
        Args:
            test_case: Test case to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation
            if test_case.input_data is None:
                return False
            
            if test_case.expected_output is None:
                return False
            
            # Allow subclasses to add specific validation
            return self._validate_test_case_constraints(test_case)
            
        except Exception:
            return False
    
    @abstractmethod
    def _validate_test_case_constraints(self, test_case: TestCase) -> bool:
        """
        Validate test case against generator-specific constraints.
        Override in subclasses.
        
        Args:
            test_case: Test case to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def generate_edge_cases(self) -> List[TestCase]:
        """
        Generate edge cases specific to this generator type.
        Override in subclasses to provide custom edge cases.
        
        Returns:
            List of edge case test cases
        """
        return []
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the generation configuration and results.
        
        Returns:
            Dictionary with generation summary
        """
        return {
            'generator_type': self.__class__.__name__,
            'seed': self.config.seed,
            'num_cases': self.config.num_cases,
            'case_types': [ct.value for ct in self.config.case_types],
            'constraints': self.config.constraints,
            'problem_id': self.config.problem_id
        }

class SimpleTestGenerator(TestGenerator):
    """
    Simple test generator for demonstration and testing purposes.
    Generates basic integer test cases.
    """
    
    def _validate_constraints(self):
        """Validate constraints for simple generator."""
        # Simple generator doesn't require specific constraints
        pass
    
    def _generate_single_case(self, case_type: TestCaseType, case_index: int) -> TestCase:
        """Generate a simple test case with integer input and doubled output."""
        min_val = self.get_constraint('min_value', 1)
        max_val = self.get_constraint('max_value', 100)
        
        if case_type == TestCaseType.EDGE:
            # Generate edge cases
            input_val = self.generate_random_choice([min_val, max_val, 0, -1])
        else:
            # Generate normal cases
            input_val = self.generate_random_int(min_val, max_val)
        
        expected_output = input_val * 2
        
        return TestCase(
            input_data=input_val,
            expected_output=expected_output,
            description=f"Simple case: {input_val} -> {expected_output}"
        )
    
    def _validate_test_case_constraints(self, test_case: TestCase) -> bool:
        """Validate simple test case constraints."""
        if not isinstance(test_case.input_data, int):
            return False
        
        if not isinstance(test_case.expected_output, int):
            return False
        
        # Check if output is correctly calculated
        return test_case.expected_output == test_case.input_data * 2
    
    def generate_edge_cases(self) -> List[TestCase]:
        """Generate edge cases for simple generator."""
        edge_cases = []
        
        # Zero case
        edge_cases.append(TestCase(
            input_data=0,
            expected_output=0,
            case_type=TestCaseType.EDGE,
            description="Edge case: zero"
        ))
        
        # Negative case
        edge_cases.append(TestCase(
            input_data=-1,
            expected_output=-2,
            case_type=TestCaseType.EDGE,
            description="Edge case: negative"
        ))
        
        return edge_cases