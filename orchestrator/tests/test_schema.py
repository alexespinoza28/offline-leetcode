"""
Unit tests for schema validation utilities.

This module tests the JSON schema validation for problem.json files
and other configuration files used throughout the platform.
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict

from orchestrator.utils.schema import SchemaValidator, load_problem_json, PROBLEM_SCHEMA


class TestSchemaValidator(unittest.TestCase):
    """Test cases for SchemaValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator()
        self.valid_problem = {
            "schema_version": "1.0.0",
            "slug": "two-sum",
            "title": "Two Sum",
            "license": "CC-BY-4.0",
            "difficulty": "Easy",
            "tags": ["array", "hash-table"],
            "io": {
                "mode": "stdin-stdout",
                "stdin_format": "Two lines: array and target",
                "stdout_format": "Two integers separated by space"
            },
            "constraints": [
                {"name": "n", "min": 2, "max": 10000, "desc": "array length"},
                {"name": "target", "value": "integer", "desc": "target sum"}
            ],
            "statement_md": "Given an array of integers, return indices of two numbers that add up to target.",
            "examples": [
                {"in": "[2,7,11,15]\n9\n", "out": "0 1\n"},
                {"in": "[3,2,4]\n6\n", "out": "1 2\n"}
            ],
            "explanation": {
                "pattern": "hashing",
                "big_o": {"time": "O(n)", "space": "O(n)"},
                "edge_cases": ["duplicate numbers", "no solution", "multiple solutions"]
            },
            "test_spec": {
                "generator": "arrays.two_sum",
                "seeds": [42, 1337, 9001],
                "sets": {
                    "small": {"count": 5, "n": [2, 10]},
                    "medium": {"count": 10, "n": [100, 1000]},
                    "large": {"count": 5, "n": [5000, 10000]}
                }
            },
            "version": "1.0.0"
        }
    
    def test_valid_problem_schema(self):
        """Test validation of a completely valid problem."""
        errors = self.validator.validate_problem(self.valid_problem)
        self.assertEqual(errors, [], f"Valid problem should have no errors: {errors}")
    
    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        required_fields = [
            "schema_version", "slug", "title", "license", "difficulty", 
            "tags", "io", "constraints", "statement_md", "examples", "version"
        ]
        
        for field in required_fields:
            with self.subTest(field=field):
                invalid_problem = self.valid_problem.copy()
                del invalid_problem[field]
                
                errors = self.validator.validate_problem(invalid_problem)
                self.assertTrue(any(field in error for error in errors),
                              f"Missing {field} should cause validation error")
    
    def test_invalid_schema_version_format(self):
        """Test validation of schema version format."""
        invalid_versions = ["1.0", "v1.0.0", "1.0.0-beta", "invalid"]
        
        for version in invalid_versions:
            with self.subTest(version=version):
                invalid_problem = self.valid_problem.copy()
                invalid_problem["schema_version"] = version
                
                errors = self.validator.validate_problem(invalid_problem)
                self.assertTrue(errors, f"Invalid schema version {version} should cause error")
    
    def test_invalid_slug_format(self):
        """Test validation of slug format."""
        invalid_slugs = ["Two Sum", "two_sum", "two-sum!", "TWO-SUM", ""]
        
        for slug in invalid_slugs:
            with self.subTest(slug=slug):
                invalid_problem = self.valid_problem.copy()
                invalid_problem["slug"] = slug
                
                errors = self.validator.validate_problem(invalid_problem)
                self.assertTrue(errors, f"Invalid slug {slug} should cause error")
    
    def test_valid_slug_format(self):
        """Test validation accepts valid slug formats."""
        valid_slugs = ["two-sum", "longest-substring", "k-sum-closest", "a", "problem-123"]
        
        for slug in valid_slugs:
            with self.subTest(slug=slug):
                valid_problem = self.valid_problem.copy()
                valid_problem["slug"] = slug
                
                errors = self.validator.validate_problem(valid_problem)
                self.assertEqual(errors, [], f"Valid slug {slug} should not cause error")
    
    def test_invalid_difficulty(self):
        """Test validation of difficulty values."""
        invalid_difficulties = ["easy", "EASY", "Normal", "Extreme", ""]
        
        for difficulty in invalid_difficulties:
            with self.subTest(difficulty=difficulty):
                invalid_problem = self.valid_problem.copy()
                invalid_problem["difficulty"] = difficulty
                
                errors = self.validator.validate_problem(invalid_problem)
                self.assertTrue(errors, f"Invalid difficulty {difficulty} should cause error")
    
    def test_valid_difficulty(self):
        """Test validation accepts valid difficulty values."""
        valid_difficulties = ["Easy", "Medium", "Hard"]
        
        for difficulty in valid_difficulties:
            with self.subTest(difficulty=difficulty):
                valid_problem = self.valid_problem.copy()
                valid_problem["difficulty"] = difficulty
                
                errors = self.validator.validate_problem(valid_problem)
                self.assertEqual(errors, [], f"Valid difficulty {difficulty} should not cause error")
    
    def test_invalid_license(self):
        """Test validation of license values."""
        invalid_licenses = ["MIT-2.0", "Custom", "Proprietary", ""]
        
        for license_val in invalid_licenses:
            with self.subTest(license=license_val):
                invalid_problem = self.valid_problem.copy()
                invalid_problem["license"] = license_val
                
                errors = self.validator.validate_problem(invalid_problem)
                self.assertTrue(errors, f"Invalid license {license_val} should cause error")
    
    def test_tags_validation(self):
        """Test validation of tags array."""
        # Test empty tags
        invalid_problem = self.valid_problem.copy()
        invalid_problem["tags"] = []
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Empty tags should cause error")
        
        # Test too many tags
        invalid_problem["tags"] = [f"tag-{i}" for i in range(15)]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Too many tags should cause error")
        
        # Test invalid tag format
        invalid_problem["tags"] = ["valid-tag", "Invalid Tag", "tag_with_underscore"]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Invalid tag format should cause error")
        
        # Test duplicate tags
        invalid_problem["tags"] = ["array", "array", "hash-table"]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Duplicate tags should cause error")
    
    def test_io_configuration_validation(self):
        """Test validation of I/O configuration."""
        # Test missing required fields
        invalid_problem = self.valid_problem.copy()
        invalid_problem["io"] = {"mode": "stdin-stdout"}
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Missing I/O fields should cause error")
        
        # Test invalid mode
        invalid_problem["io"] = {
            "mode": "invalid-mode",
            "stdin_format": "test",
            "stdout_format": "test"
        }
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Invalid I/O mode should cause error")
        
        # Test function mode without signature
        invalid_problem["io"] = {
            "mode": "function",
            "stdin_format": "test",
            "stdout_format": "test"
        }
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Function mode without signature should cause error")
    
    def test_constraints_validation(self):
        """Test validation of constraints."""
        # Test constraint with min > max
        invalid_problem = self.valid_problem.copy()
        invalid_problem["constraints"] = [
            {"name": "n", "min": 100, "max": 10, "desc": "invalid range"}
        ]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Constraint with min > max should cause error")
        
        # Test constraint without min/max or value
        invalid_problem["constraints"] = [
            {"name": "n", "desc": "missing range or value"}
        ]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Constraint without range or value should cause error")
        
        # Test invalid constraint name
        invalid_problem["constraints"] = [
            {"name": "123invalid", "min": 1, "max": 10, "desc": "invalid name"}
        ]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Invalid constraint name should cause error")
    
    def test_examples_validation(self):
        """Test validation of examples."""
        # Test empty examples
        invalid_problem = self.valid_problem.copy()
        invalid_problem["examples"] = []
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Empty examples should cause error")
        
        # Test too many examples
        invalid_problem["examples"] = [
            {"in": f"input{i}", "out": f"output{i}"} for i in range(15)
        ]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Too many examples should cause error")
        
        # Test missing required fields in examples
        invalid_problem["examples"] = [{"in": "input"}]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Example missing output should cause error")
    
    def test_test_spec_validation(self):
        """Test validation of test specification."""
        # Test duplicate seeds
        invalid_problem = self.valid_problem.copy()
        invalid_problem["test_spec"]["seeds"] = [42, 42, 1337]
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Duplicate seeds should cause error")
        
        # Test invalid generator format
        invalid_problem["test_spec"]["generator"] = "invalid_generator"
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Invalid generator format should cause error")
    
    def test_explanation_validation(self):
        """Test validation of explanation metadata."""
        # Test invalid pattern
        invalid_problem = self.valid_problem.copy()
        invalid_problem["explanation"]["pattern"] = "invalid_pattern"
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Invalid explanation pattern should cause error")
        
        # Test invalid big_o format
        invalid_problem["explanation"]["big_o"] = {"time": "O(n", "space": "O(1)"}
        errors = self.validator.validate_problem(invalid_problem)
        self.assertTrue(errors, "Invalid big_o format should cause error")


class TestProblemFileLoading(unittest.TestCase):
    """Test cases for problem file loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_problem_data = {
            "schema_version": "1.0.0",
            "slug": "test-problem",
            "title": "Test Problem",
            "license": "CC-BY-4.0",
            "difficulty": "Easy",
            "tags": ["test"],
            "io": {
                "mode": "stdin-stdout",
                "stdin_format": "test input",
                "stdout_format": "test output"
            },
            "constraints": [
                {"name": "n", "min": 1, "max": 100, "desc": "test constraint"}
            ],
            "statement_md": "Test problem statement",
            "examples": [
                {"in": "test input", "out": "test output"}
            ],
            "version": "1.0.0"
        }
    
    def test_load_valid_problem_file(self):
        """Test loading a valid problem.json file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_problem_data, f)
            temp_path = Path(f.name)
        
        try:
            problem_data = load_problem_json(temp_path)
            self.assertEqual(problem_data["slug"], "test-problem")
            self.assertEqual(problem_data["title"], "Test Problem")
        finally:
            temp_path.unlink()
    
    def test_load_invalid_json_file(self):
        """Test loading a file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)
        
        try:
            with self.assertRaises(ValueError) as context:
                load_problem_json(temp_path)
            self.assertIn("Problem validation failed", str(context.exception))
        finally:
            temp_path.unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        nonexistent_path = Path("/nonexistent/problem.json")
        
        with self.assertRaises(ValueError) as context:
            load_problem_json(nonexistent_path)
        self.assertIn("Problem validation failed", str(context.exception))
    
    def test_load_invalid_problem_data(self):
        """Test loading a file with invalid problem data."""
        invalid_data = {"invalid": "data"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_path = Path(f.name)
        
        try:
            with self.assertRaises(ValueError) as context:
                load_problem_json(temp_path)
            self.assertIn("Problem validation failed", str(context.exception))
        finally:
            temp_path.unlink()


class TestProblemSchema(unittest.TestCase):
    """Test cases for the problem JSON schema definition."""
    
    def test_schema_structure(self):
        """Test that the schema has the expected structure."""
        self.assertIn("$schema", PROBLEM_SCHEMA)
        self.assertEqual(PROBLEM_SCHEMA["type"], "object")
        self.assertIn("required", PROBLEM_SCHEMA)
        self.assertIn("properties", PROBLEM_SCHEMA)
    
    def test_required_fields(self):
        """Test that all expected fields are required."""
        expected_required = [
            "schema_version", "slug", "title", "license", "difficulty",
            "tags", "io", "constraints", "statement_md", "examples", "version"
        ]
        
        for field in expected_required:
            self.assertIn(field, PROBLEM_SCHEMA["required"],
                         f"Field {field} should be required")
    
    def test_property_definitions(self):
        """Test that key properties have proper definitions."""
        properties = PROBLEM_SCHEMA["properties"]
        
        # Test slug pattern
        self.assertIn("pattern", properties["slug"])
        self.assertEqual(properties["slug"]["pattern"], "^[a-z0-9-]+$")
        
        # Test difficulty enum
        self.assertIn("enum", properties["difficulty"])
        self.assertEqual(set(properties["difficulty"]["enum"]), 
                        {"Easy", "Medium", "Hard"})
        
        # Test tags array constraints
        tags_prop = properties["tags"]
        self.assertEqual(tags_prop["type"], "array")
        self.assertTrue(tags_prop["uniqueItems"])
        self.assertEqual(tags_prop["minItems"], 1)
        self.assertEqual(tags_prop["maxItems"], 10)


if __name__ == '__main__':
    unittest.main()