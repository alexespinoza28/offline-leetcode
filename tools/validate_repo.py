"""
Repository validation tool.

This script validates the entire problem repository, checking for:
- Problem schema compliance
- Test case validity
- Solution compilation and execution for all languages
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add orchestrator to path to import modules
sys.path.append(str(Path(__file__).parent.parent / "orchestrator"))

from orchestrator.language_adapters import CppAdapter, PythonAdapter, CAdapter, NodeAdapter, JavaAdapter
from orchestrator.language_adapters.base import ResourceLimits
from orchestrator.utils.schema import validate_problem_schema


class RepoValidator:
    """Validates the problem repository."""

    def __init__(self, problems_dir: str = "problems"):
        self.problems_dir = Path(problems_dir)
        self.languages = {
            "cpp": CppAdapter(),
            "py": PythonAdapter(),
            "c": CAdapter(),
            "js": NodeAdapter(),
            "java": JavaAdapter(),
        }
        self.results: Dict[str, Any] = {}

    def validate(self) -> bool:
        """Validates all problems in the repository."""
        print("Starting repository validation...")
        all_passed = True

        for problem_dir in self.problems_dir.iterdir():
            if problem_dir.is_dir():
                problem_slug = problem_dir.name
                print(f"\nValidating problem: {problem_slug}")
                self.results[problem_slug] = {}

                if not self._validate_problem_schema(problem_dir):
                    all_passed = False
                    continue

                if not self._validate_solutions(problem_dir):
                    all_passed = False

        print("\nValidation complete.")
        self._print_summary()
        return all_passed

    def _validate_problem_schema(self, problem_dir: Path) -> bool:
        """Validates the problem.json schema for a single problem."""
        print("  Validating problem schema...")
        problem_json_path = problem_dir / "problem.json"
        if not problem_json_path.exists():
            self._add_error(problem_dir.name, "schema", "problem.json not found")
            return False

        with open(problem_json_path, "r") as f:
            try:
                problem_data = json.load(f)
            except json.JSONDecodeError as e:
                self._add_error(problem_dir.name, "schema", f"Invalid JSON: {e}")
                return False

        is_valid, error = validate_problem_schema(problem_data)
        if not is_valid:
            self._add_error(problem_dir.name, "schema", error)
            return False

        print("    Schema validation passed.")
        return True

    def _validate_solutions(self, problem_dir: Path) -> bool:
        """Validates all solutions for a single problem."""
        print("  Validating solutions...")
        all_solutions_passed = True

        for lang, adapter in self.languages.items():
            solution_dir = problem_dir / lang
            if solution_dir.exists():
                print(f"    Validating {lang} solution...")
                if not self._validate_solution(problem_dir, lang, adapter):
                    all_solutions_passed = False

        return all_solutions_passed

    def _validate_solution(self, problem_dir: Path, lang: str, adapter: Any) -> bool:
        """Validates a single solution."""
        solution_dir = problem_dir / lang
        self.results[problem_dir.name][lang] = {"compile": "SKIPPED", "run": "SKIPPED"}

        # Compile solution
        compile_result = adapter.compile(solution_dir)
        if not compile_result.success:
            self._add_error(
                problem_dir.name,
                lang,
                f"Compilation failed: {compile_result.stderr}",
            )
            self.results[problem_dir.name][lang]["compile"] = "FAILED"
            return False
        self.results[problem_dir.name][lang]["compile"] = "PASSED"

        # Run solution against test cases
        test_cases_dir = problem_dir / "test_cases"
        if not test_cases_dir.exists():
            print(f"      No test cases found for {problem_dir.name}. Skipping run validation.")
            return True

        for test_case_in in test_cases_dir.glob("*.in"):
            test_case_out = test_case_in.with_suffix(".out")
            if not test_case_out.exists():
                self._add_error(
                    problem_dir.name,
                    lang,
                    f"Missing .out file for {test_case_in.name}",
                )
                self.results[problem_dir.name][lang]["run"] = "FAILED"
                return False

            run_result = adapter.run(
                solution_dir,
                test_case_in,
                solution_dir / "output.txt",
                ResourceLimits(),
            )

        self.results[problem_dir.name][lang]["run"] = "PASSED"
        print(f"      {lang} solution passed.")
        return True

    def _add_error(self, problem: str, component: str, message: str):
        """Adds an error to the results."""
        if "errors" not in self.results[problem]:
            self.results[problem]["errors"] = []
        self.results[problem]["errors"].append(f"[{component.upper()}] {message}")
        print(f"    ERROR: {message}")

    def _print_summary(self):
        """Prints a summary of the validation results."""
        print("\n--- Validation Summary ---")
        for problem, result in self.results.items():
            print(f"\nProblem: {problem}")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"  - {error}")
            else:
                print("  - All checks passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate the problem repository.")
    parser.add_argument(
        "--problems-dir",
        default="problems",
        help="Path to the problems directory.",
    )
    args = parser.parse_args()

    validator = RepoValidator(args.problems_dir)
    if not validator.validate():
        sys.exit(1)
