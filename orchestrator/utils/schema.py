"""
JSON schema validation utilities for problem definitions.

This module provides schema validation for problem.json files and other
configuration files used throughout the platform.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jsonschema
from jsonschema import Draft7Validator


# Problem JSON Schema Definition
PROBLEM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": [
        "schema_version",
        "slug",
        "title",
        "license",
        "difficulty",
        "tags",
        "io",
        "constraints",
        "statement_md",
        "examples",
        "version"
    ],
    "properties": {
        "schema_version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$",
            "description": "Schema version for compatibility"
        },
        "slug": {
            "type": "string",
            "pattern": "^[a-z0-9-]+$",
            "minLength": 1,
            "maxLength": 100,
            "description": "Unique problem identifier"
        },
        "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200,
            "description": "Human-readable problem title"
        },
        "license": {
            "type": "string",
            "enum": ["CC-BY-4.0", "MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"],
            "description": "Problem license"
        },
        "difficulty": {
            "type": "string",
            "enum": ["Easy", "Medium", "Hard"],
            "description": "Problem difficulty level"
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[a-z0-9-]+$"
            },
            "minItems": 1,
            "maxItems": 10,
            "uniqueItems": True,
            "description": "Problem tags for categorization"
        },
        "io": {
            "type": "object",
            "required": ["mode", "stdin_format", "stdout_format"],
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["stdin-stdout", "function"],
                    "description": "Input/output mode"
                },
                "stdin_format": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Description of input format"
                },
                "stdout_format": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Description of output format"
                },
                "signature": {
                    "type": "object",
                    "properties": {
                        "language_signatures": {
                            "type": "object",
                            "patternProperties": {
                                "^(c|cpp|py|js|java)$": {
                                    "type": "string",
                                    "minLength": 1
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "description": "Function signatures for function mode"
                }
            },
            "additionalProperties": False
        },
        "constraints": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "desc"],
                "properties": {
                    "name": {
                        "type": "string",
                        "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"
                    },
                    "min": {
                        "type": "integer"
                    },
                    "max": {
                        "type": "integer"
                    },
                    "value": {
                        "type": "string"
                    },
                    "desc": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "additionalProperties": False
            },
            "description": "Problem constraints"
        },
        "statement_md": {
            "type": "string",
            "minLength": 10,
            "description": "Problem statement in markdown"
        },
        "examples": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["in", "out"],
                "properties": {
                    "in": {
                        "type": "string"
                    },
                    "out": {
                        "type": "string"
                    }
                },
                "additionalProperties": False
            },
            "minItems": 1,
            "maxItems": 10,
            "description": "Example input/output pairs"
        },
        "explanation": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "enum": [
                        "sliding_window", "two_pointers", "dynamic_programming",
                        "greedy", "backtracking", "divide_conquer", "graph_traversal",
                        "binary_search", "sorting", "hashing", "tree_traversal",
                        "string_matching", "bit_manipulation", "math"
                    ]
                },
                "big_o": {
                    "type": "object",
                    "properties": {
                        "time": {
                            "type": "string",
                            "pattern": "^O\\(.+\\)$"
                        },
                        "space": {
                            "type": "string",
                            "pattern": "^O\\(.+\\)$"
                        }
                    }
                },
                "edge_cases": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "description": "Explanation metadata for template generation"
        },
        "test_spec": {
            "type": "object",
            "properties": {
                "generator": {
                    "type": "string",
                    "pattern": "^[a-z_]+\\.[a-z_]+$"
                },
                "seeds": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "minItems": 1,
                    "maxItems": 10,
                    "uniqueItems": True
                },
                "sets": {
                    "type": "object",
                    "patternProperties": {
                        "^(small|medium|large)$": {
                            "type": "object",
                            "required": ["count"],
                            "properties": {
                                "count": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 100
                                }
                            },
                            "additionalProperties": True
                        }
                    },
                    "additionalProperties": False
                }
            },
            "description": "Test generation specification"
        },
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$",
            "description": "Problem version for tracking changes"
        }
    },
    "additionalProperties": False
}


class SchemaValidator:
    """Validates JSON data against predefined schemas."""
    
    def __init__(self):
        """Initialize the validator with compiled schemas."""
        self.problem_validator = Draft7Validator(PROBLEM_SCHEMA)
    
    def validate_problem(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate problem.json data against the schema.
        
        Args:
            data: Problem data dictionary
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Basic schema validation
        for error in self.problem_validator.iter_errors(data):
            errors.append(f"Schema error at {'.'.join(str(p) for p in error.absolute_path)}: {error.message}")
        
        # Additional business logic validation
        if not errors:
            errors.extend(self._validate_problem_constraints(data))
            errors.extend(self._validate_problem_consistency(data))
        
        return errors
    
    def _validate_problem_constraints(self, data: Dict[str, Any]) -> List[str]:
        """Validate constraint definitions."""
        errors = []
        
        constraints = data.get("constraints", [])
        for i, constraint in enumerate(constraints):
            # Check min/max consistency
            if "min" in constraint and "max" in constraint:
                if constraint["min"] > constraint["max"]:
                    errors.append(f"Constraint {i}: min ({constraint['min']}) > max ({constraint['max']})")
            
            # Ensure either min/max or value is specified
            has_range = "min" in constraint or "max" in constraint
            has_value = "value" in constraint
            if not has_range and not has_value:
                errors.append(f"Constraint {i}: must specify either min/max range or fixed value")
        
        return errors
    
    def _validate_problem_consistency(self, data: Dict[str, Any]) -> List[str]:
        """Validate internal consistency of problem data."""
        errors = []
        
        # Check test_spec seeds are unique
        test_spec = data.get("test_spec", {})
        seeds = test_spec.get("seeds", [])
        if len(seeds) != len(set(seeds)):
            errors.append("test_spec.seeds must contain unique values")
        
        # Validate function mode consistency
        io_config = data.get("io", {})
        if io_config.get("mode") == "function":
            if "signature" not in io_config:
                errors.append("Function mode requires signature specification")
            elif "language_signatures" not in io_config["signature"]:
                errors.append("Function mode requires language_signatures")
        
        return errors
    
    def validate_problem_file(self, file_path: Path) -> List[str]:
        """
        Validate a problem.json file.
        
        Args:
            file_path: Path to problem.json file
            
        Returns:
            List of validation error messages
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self.validate_problem(data)
        except json.JSONDecodeError as e:
            return [f"Invalid JSON: {e}"]
        except FileNotFoundError:
            return [f"File not found: {file_path}"]
        except Exception as e:
            return [f"Error reading file: {e}"]


def load_problem_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load and validate a problem.json file.
    
    Args:
        file_path: Path to problem.json file
        
    Returns:
        Problem data dictionary if valid, None otherwise
    """
    validator = SchemaValidator()
    errors = validator.validate_problem_file(file_path)
    
    if errors:
        raise ValueError(f"Problem validation failed: {'; '.join(errors)}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)