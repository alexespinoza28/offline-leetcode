#!/usr/bin/env python3
"""
Simple test script for gen_tests.py functionality without pytest dependency.
"""

import json
import tempfile
import subprocess
import sys
import shutil
from pathlib import Path

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from gen_tests import TestGenerator, TestGenerationError

def test_basic_generation():
    """Test basic test generation functionality."""
    print("Testing basic test generation...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    problem_dir = Path(temp_dir) / "test_problem"
    problem_dir.mkdir(parents=True)
    
    try:
        # Create problem specification
        problem_spec = {
            "slug": "test-problem",
            "title": "Test Problem",
            "test_spec": {
                "num_cases": 3,
                "case_types": ["unit"],
                "constraints": {
                    "min_value": 1,
                    "max_value": 10
                }
            }
        }
        
        problem_file = problem_dir / "problem.json"
        with open(problem_file, 'w') as f:
            json.dump(problem_spec, f, indent=2)
        
        # Create reference solution
        reference_code = """import sys
n = int(input().strip())
print(n * 2)
"""
        solution_file = problem_dir / "solution.py"
        with open(solution_file, 'w') as f:
            f.write(reference_code)
        
        # Generate tests
        generator = TestGenerator(problem_dir)
        result = generator.generate_tests(generator_type="simple", seed=42)
        
        # Verify results
        assert result["status"] == "success", f"Expected success, got {result['status']}"
        assert result["num_cases"] == 3, f"Expected 3 cases, got {result['num_cases']}"
        assert result["generator"] == "SimpleTestGenerator", f"Expected SimpleTestGenerator, got {result['generator']}"
        
        # Check that files were created
        output_dir = Path(result["output_dir"])
        assert output_dir.exists(), "Output directory should exist"
        
        # Check for input files
        unit_dir = output_dir / "unit"
        input_files = list(unit_dir.glob("*.in"))
        assert len(input_files) == 3, f"Expected 3 input files, got {len(input_files)}"
        
        # Check for output files
        output_files = list(unit_dir.glob("*.out"))
        assert len(output_files) == 3, f"Expected 3 output files, got {len(output_files)}"
        
        # Check metadata file
        metadata_file = output_dir / "generation_metadata.json"
        assert metadata_file.exists(), "Metadata file should exist"
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        assert metadata["generator"]["type"] == "SimpleTestGenerator"
        assert len(metadata["test_cases"]) == 3
        
        print("✓ Basic test generation passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def test_string_generation():
    """Test string generator functionality."""
    print("Testing string test generation...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    problem_dir = Path(temp_dir) / "string_problem"
    problem_dir.mkdir(parents=True)
    
    try:
        # Create problem specification
        problem_spec = {
            "slug": "string-problem",
            "title": "String Problem",
            "test_spec": {
                "num_cases": 4,
                "case_types": ["unit"],
                "string": {
                    "min_length": 3,
                    "max_length": 8,
                    "charset": "lowercase",
                    "patterns": ["random"],
                    "ensure_coverage": False
                }
            }
        }
        
        problem_file = problem_dir / "problem.json"
        with open(problem_file, 'w') as f:
            json.dump(problem_spec, f, indent=2)
        
        # Create reference solution for string reversal
        reference_code = """s = input().strip()
print(s[::-1])
"""
        solution_file = problem_dir / "solution.py"
        with open(solution_file, 'w') as f:
            f.write(reference_code)
        
        # Generate tests
        generator = TestGenerator(problem_dir)
        result = generator.generate_tests(generator_type="string", seed=42)
        
        # Verify results
        assert result["status"] == "success", f"Expected success, got {result['status']}"
        assert result["num_cases"] == 4, f"Expected 4 cases, got {result['num_cases']}"
        assert result["generator"] == "StringTestGenerator", f"Expected StringTestGenerator, got {result['generator']}"
        
        # Check that string inputs were generated
        output_dir = Path(result["output_dir"])
        unit_dir = output_dir / "unit"
        
        input_files = list(unit_dir.glob("*.in"))
        assert len(input_files) == 4, f"Expected 4 input files, got {len(input_files)}"
        
        # Verify input content is strings
        for input_file in input_files:
            with open(input_file) as f:
                content = f.read().strip()
                assert 3 <= len(content) <= 8, f"String length {len(content)} not in range [3, 8]"
                assert all(c.islower() for c in content), f"String '{content}' contains non-lowercase characters"
        
        print("✓ String test generation passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def test_cli_integration():
    """Test CLI integration."""
    print("Testing CLI integration...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    problem_dir = Path(temp_dir) / "cli_test_problem"
    problem_dir.mkdir(parents=True)
    
    try:
        # Create problem specification
        problem_spec = {
            "slug": "cli-test-problem",
            "title": "CLI Test Problem",
            "test_spec": {
                "num_cases": 2,
                "case_types": ["unit"],
                "string": {
                    "min_length": 2,
                    "max_length": 5,
                    "charset": "abc"
                }
            }
        }
        
        problem_file = problem_dir / "problem.json"
        with open(problem_file, 'w') as f:
            json.dump(problem_spec, f, indent=2)
        
        # Create reference solution
        reference_code = """s = input().strip()
print(s.upper())
"""
        solution_file = problem_dir / "solution.py"
        with open(solution_file, 'w') as f:
            f.write(reference_code)
        
        # Run CLI tool
        gen_tests_script = Path(__file__).parent / "gen_tests.py"
        cmd = [
            sys.executable, str(gen_tests_script),
            str(problem_dir),
            "--type", "string",
            "--seed", "42"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        assert result.returncode == 0, f"CLI failed with return code {result.returncode}. stderr: {result.stderr}"
        assert "Generated 2 test cases" in result.stdout, f"Expected success message in stdout: {result.stdout}"
        assert "StringTestGenerator" in result.stdout, f"Expected generator name in stdout: {result.stdout}"
        
        # Check that files were created
        output_dir = problem_dir / "tests"
        assert output_dir.exists(), "Output directory should exist"
        
        unit_dir = output_dir / "unit"
        input_files = list(unit_dir.glob("*.in"))
        output_files = list(unit_dir.glob("*.out"))
        
        assert len(input_files) == 2, f"Expected 2 input files, got {len(input_files)}"
        assert len(output_files) == 2, f"Expected 2 output files, got {len(output_files)}"
        
        print("✓ CLI integration test passed")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def test_error_handling():
    """Test error handling."""
    print("Testing error handling...")
    
    # Test with non-existent directory
    try:
        generator = TestGenerator(Path("/non/existent/directory"))
        generator.generate_tests()
        assert False, "Should have raised TestGenerationError"
    except TestGenerationError:
        print("✓ Error handling for missing directory passed")
    
    # Test with invalid problem.json
    temp_dir = tempfile.mkdtemp()
    problem_dir = Path(temp_dir) / "invalid_problem"
    problem_dir.mkdir(parents=True)
    
    try:
        # Create invalid JSON
        problem_file = problem_dir / "problem.json"
        with open(problem_file, 'w') as f:
            f.write("{ invalid json")
        
        generator = TestGenerator(problem_dir)
        try:
            generator.generate_tests()
            assert False, "Should have raised TestGenerationError"
        except TestGenerationError:
            print("✓ Error handling for invalid JSON passed")
        
    finally:
        shutil.rmtree(temp_dir)

def main():
    """Run all tests."""
    print("Running gen_tests.py integration tests...")
    print("=" * 50)
    
    try:
        test_basic_generation()
        test_string_generation()
        test_cli_integration()
        test_error_handling()
        
        print("=" * 50)
        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()