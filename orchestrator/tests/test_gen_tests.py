"""
Integration tests for the test generation CLI tool.
"""

import pytest
import json
import tempfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gen_tests import TestGenerator, TestGenerationError

class TestTestGenerator:
    """Test cases for TestGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.problem_dir = Path(self.temp_dir) / "test_problem"
        self.problem_dir.mkdir(parents=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_problem_json(self, problem_spec: dict):
        """Create a problem.json file with the given specification."""
        problem_file = self.problem_dir / "problem.json"
        with open(problem_file, 'w') as f:
            json.dump(problem_spec, f, indent=2)
    
    def create_reference_solution(self, code: str, filename: str = "solution.py"):
        """Create a reference solution file."""
        solution_file = self.problem_dir / filename
        with open(solution_file, 'w') as f:
            f.write(code)
        return solution_file
    
    def test_basic_test_generation(self):
        """Test basic test generation with simple generator."""
        # Create problem specification
        problem_spec = {
            "slug": "test-problem",
            "title": "Test Problem",
            "test_spec": {
                "num_cases": 5,
                "case_types": ["unit"],
                "constraints": {
                    "min_value": 1,
                    "max_value": 10
                }
            }
        }
        self.create_problem_json(problem_spec)
        
        # Create reference solution
        reference_code = """
import sys
n = int(input().strip())
print(n * 2)
"""
        self.create_reference_solution(reference_code)
        
        # Generate tests
        generator = TestGenerator(self.problem_dir)
        result = generator.generate_tests(generator_type="simple", seed=42)
        
        assert result["status"] == "success"
        assert result["num_cases"] == 5
        assert result["generator"] == "SimpleTestGenerator"
        
        # Check that files were created
        output_dir = Path(result["output_dir"])
        assert output_dir.exists()
        
        # Check for input files
        unit_dir = output_dir / "unit"
        input_files = list(unit_dir.glob("*.in"))
        assert len(input_files) == 5
        
        # Check for output files
        output_files = list(unit_dir.glob("*.out"))
        assert len(output_files) == 5
        
        # Check metadata file
        metadata_file = output_dir / "generation_metadata.json"
        assert metadata_file.exists()
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        assert metadata["generator"]["type"] == "SimpleTestGenerator"
        assert len(metadata["test_cases"]) == 5
    
    def test_string_generator(self):
        """Test string generator with string-specific configuration."""
        problem_spec = {
            "slug": "string-problem",
            "title": "String Problem",
            "test_spec": {
                "num_cases": 4,
                "case_types": ["unit", "edge"],
                "string": {
                    "min_length": 3,
                    "max_length": 8,
                    "charset": "lowercase",
                    "patterns": ["palindrome", "random"],
                    "ensure_coverage": False
                }
            }
        }
        self.create_problem_json(problem_spec)
        
        # Create reference solution for string reversal
        reference_code = """
s = input().strip()
print(s[::-1])
"""
        self.create_reference_solution(reference_code)
        
        # Generate tests
        generator = TestGenerator(self.problem_dir)
        result = generator.generate_tests(generator_type="string", seed=42)
        
        assert result["status"] == "success"
        assert result["num_cases"] == 4
        assert result["generator"] == "StringTestGenerator"
        
        # Check that string inputs were generated
        output_dir = Path(result["output_dir"])
        unit_dir = output_dir / "unit"
        
        input_files = list(unit_dir.glob("*.in"))
        assert len(input_files) == 4
        
        # Verify input content is strings
        for input_file in input_files:
            with open(input_file) as f:
                content = f.read().strip()
                assert 3 <= len(content) <= 8
                assert all(c.islower() for c in content)
    
    def test_cover_all_chars_generator(self):
        """Test cover all chars generator."""
        problem_spec = {
            "slug": "coverage-problem",
            "title": "Coverage Problem",
            "test_spec": {
                "num_cases": 3,
                "string": {
                    "min_length": 2,
                    "max_length": 4,
                    "charset": "abc",
                    "ensure_coverage": True
                }
            }
        }
        self.create_problem_json(problem_spec)
        
        # Create reference solution
        reference_code = """
s = input().strip()
print(len(s))
"""
        self.create_reference_solution(reference_code)
        
        # Generate tests
        generator = TestGenerator(self.problem_dir)
        result = generator.generate_tests(generator_type="cover_all_chars", seed=42)
        
        assert result["status"] == "success"
        assert result["generator"] == "CoverAllCharsGenerator"
        
        # Check coverage in metadata
        metadata_file = Path(result["output_dir"]) / "generation_metadata.json"
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        if "coverage" in metadata:
            coverage = metadata["coverage"]
            assert coverage["total_characters"] == 3  # 'a', 'b', 'c'
            assert coverage["coverage_percentage"] >= 0
    
    def test_auto_detection(self):
        """Test automatic generator detection."""
        # Problem with string spec should auto-detect string generator
        problem_spec = {
            "slug": "auto-problem",
            "title": "Auto Detection Problem",
            "test_spec": {
                "num_cases": 3,
                "string": {
                    "min_length": 2,
                    "max_length": 5,
                    "charset": "digits"
                }
            }
        }
        self.create_problem_json(problem_spec)
        
        # Create reference solution
        reference_code = """
s = input().strip()
print(s)
"""
        self.create_reference_solution(reference_code)
        
        # Generate tests with auto detection
        generator = TestGenerator(self.problem_dir)
        result = generator.generate_tests(generator_type="auto", seed=42)
        
        assert result["status"] == "success"
        assert result["generator"] == "StringTestGenerator"
    
    def test_no_reference_solution(self):
        """Test generation without reference solution."""
        problem_spec = {
            "slug": "no-ref-problem",
            "title": "No Reference Problem",
            "test_spec": {
                "num_cases": 3
            }
        }
        self.create_problem_json(problem_spec)
        
        # Don't create reference solution
        
        # Generate tests
        generator = TestGenerator(self.problem_dir)
        result = generator.generate_tests(generator_type="simple", seed=42)
        
        assert result["status"] == "success"
        assert result["num_cases"] == 3
        
        # Should have input files but no output files
        output_dir = Path(result["output_dir"])
        unit_dir = output_dir / "unit"
        
        input_files = list(unit_dir.glob("*.in"))
        output_files = list(unit_dir.glob("*.out"))
        
        assert len(input_files) == 3
        assert len(output_files) == 0  # No reference solution
    
    def test_cpp_reference_solution(self):
        """Test with C++ reference solution."""
        problem_spec = {
            "slug": "cpp-problem",
            "title": "C++ Problem",
            "test_spec": {
                "num_cases": 2,
                "constraints": {
                    "min_value": 1,
                    "max_value": 5
                }
            }
        }
        self.create_problem_json(problem_spec)
        
        # Create C++ reference solution
        cpp_code = """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * 3 << endl;
    return 0;
}
"""
        self.create_reference_solution(cpp_code, "solution.cpp")
        
        # Mock the C++ adapter to avoid actual compilation
        with patch('gen_tests.CppAdapter') as mock_adapter_class:
            mock_adapter = MagicMock()
            mock_adapter_class.return_value = mock_adapter
            
            # Mock successful compilation
            mock_compile_result = MagicMock()
            mock_compile_result.success = True
            mock_adapter.compile.return_value = mock_compile_result
            
            # Mock successful execution
            mock_run_result = MagicMock()
            mock_run_result.success = True
            mock_run_result.stdout = "6\n"  # 2 * 3
            mock_adapter.run.return_value = mock_run_result
            
            # Generate tests
            generator = TestGenerator(self.problem_dir)
            result = generator.generate_tests(generator_type="simple", seed=42)
            
            assert result["status"] == "success"
            
            # Verify adapter was called
            mock_adapter.compile.assert_called()
            mock_adapter.run.assert_called()
    
    def test_existing_tests_skip(self):
        """Test that existing tests are skipped unless force is used."""
        problem_spec = {
            "slug": "existing-problem",
            "title": "Existing Problem",
            "test_spec": {
                "num_cases": 2
            }
        }
        self.create_problem_json(problem_spec)
        
        # Create existing test files
        output_dir = self.problem_dir / "tests" / "unit"
        output_dir.mkdir(parents=True)
        (output_dir / "01.in").write_text("1\n")
        
        # Generate tests without force
        generator = TestGenerator(self.problem_dir)
        result = generator.generate_tests(generator_type="simple", seed=42, force=False)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "tests_exist"
        
        # Generate tests with force
        result = generator.generate_tests(generator_type="simple", seed=42, force=True)
        
        assert result["status"] == "success"
    
    def test_invalid_problem_json(self):
        """Test error handling for invalid problem.json."""
        # Create invalid JSON
        problem_file = self.problem_dir / "problem.json"
        with open(problem_file, 'w') as f:
            f.write("{ invalid json")
        
        generator = TestGenerator(self.problem_dir)
        
        with pytest.raises(TestGenerationError):
            generator.generate_tests()
    
    def test_missing_problem_json(self):
        """Test error handling for missing problem.json."""
        # Don't create problem.json
        
        generator = TestGenerator(self.problem_dir)
        
        with pytest.raises(TestGenerationError):
            generator.generate_tests()
    
    def test_different_case_types(self):
        """Test generation with different case types."""
        problem_spec = {
            "slug": "case-types-problem",
            "title": "Case Types Problem",
            "test_spec": {
                "num_cases": 6,
                "case_types": ["sample", "unit", "hidden"]
            }
        }
        self.create_problem_json(problem_spec)
        
        # Create reference solution
        reference_code = """
n = int(input().strip())
print(n + 1)
"""
        self.create_reference_solution(reference_code)
        
        # Generate tests
        generator = TestGenerator(self.problem_dir)
        result = generator.generate_tests(generator_type="simple", seed=42)
        
        assert result["status"] == "success"
        
        # Check that different directories were created
        output_dir = Path(result["output_dir"])
        assert (output_dir / "sample").exists()
        assert (output_dir / "unit").exists()
        assert (output_dir / "hidden").exists()
        
        # Check that files are distributed across directories
        sample_files = list((output_dir / "sample").glob("*.in"))
        unit_files = list((output_dir / "unit").glob("*.in"))
        hidden_files = list((output_dir / "hidden").glob("*.in"))
        
        total_files = len(sample_files) + len(unit_files) + len(hidden_files)
        assert total_files == 6

class TestCLIIntegration:
    """Integration tests for the CLI interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.problem_dir = Path(self.temp_dir) / "cli_test_problem"
        self.problem_dir.mkdir(parents=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_problem(self):
        """Create a test problem for CLI testing."""
        problem_spec = {
            "slug": "cli-test-problem",
            "title": "CLI Test Problem",
            "test_spec": {
                "num_cases": 3,
                "case_types": ["unit"],
                "string": {
                    "min_length": 2,
                    "max_length": 5,
                    "charset": "abc"
                }
            }
        }
        
        problem_file = self.problem_dir / "problem.json"
        with open(problem_file, 'w') as f:
            json.dump(problem_spec, f, indent=2)
        
        # Create reference solution
        reference_code = """
s = input().strip()
print(s.upper())
"""
        solution_file = self.problem_dir / "solution.py"
        with open(solution_file, 'w') as f:
            f.write(reference_code)
    
    def test_cli_basic_usage(self):
        """Test basic CLI usage."""
        self.create_test_problem()
        
        # Run CLI tool
        gen_tests_script = Path(__file__).parent.parent / "gen_tests.py"
        cmd = [
            sys.executable, str(gen_tests_script),
            str(self.problem_dir),
            "--type", "string",
            "--seed", "42"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Generated 3 test cases" in result.stdout
        assert "StringTestGenerator" in result.stdout
        
        # Check that files were created
        output_dir = self.problem_dir / "tests"
        assert output_dir.exists()
        
        unit_dir = output_dir / "unit"
        input_files = list(unit_dir.glob("*.in"))
        output_files = list(unit_dir.glob("*.out"))
        
        assert len(input_files) == 3
        assert len(output_files) == 3
    
    def test_cli_help(self):
        """Test CLI help output."""
        gen_tests_script = Path(__file__).parent.parent / "gen_tests.py"
        cmd = [sys.executable, str(gen_tests_script), "--help"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Generate test cases for coding problems" in result.stdout
        assert "--type" in result.stdout
        assert "--num-cases" in result.stdout
    
    def test_cli_error_handling(self):
        """Test CLI error handling."""
        # Test with non-existent directory
        gen_tests_script = Path(__file__).parent.parent / "gen_tests.py"
        cmd = [
            sys.executable, str(gen_tests_script),
            "/non/existent/directory"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        assert result.returncode == 1
        assert "ERROR:" in result.stderr

if __name__ == "__main__":
    pytest.main([__file__])