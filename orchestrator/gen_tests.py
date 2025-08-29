#!/usr/bin/env python3
"""
Test generation CLI tool for creating test cases from problem specifications.

This tool reads problem.json files with test_spec configurations and generates
test cases using the appropriate generators, then executes reference solutions
to create expected output files.
"""

import argparse
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

# Add the orchestrator directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from testing.generators import (
    StringTestGenerator, StringGeneratorConfig, StringPattern,
    CoverAllCharsGenerator, ReverseStringGenerator, UppercaseGenerator,
    LowercaseGenerator, PalindromeCheckGenerator, CharacterCountGenerator,
    StringLengthGenerator, SimpleTestGenerator, GeneratorConfig, TestCaseType
)
from language_adapters.python import PythonAdapter
from language_adapters.cpp import CppAdapter
from utils.schema import SchemaValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class TestGenerationError(Exception):
    """Exception raised during test generation."""
    pass

class TestGenerator:
    """Main test generation orchestrator."""
    
    def __init__(self, problem_dir: Path, output_dir: Optional[Path] = None):
        """
        Initialize test generator.
        
        Args:
            problem_dir: Directory containing problem.json
            output_dir: Output directory for generated tests (default: problem_dir/tests)
        """
        self.problem_dir = Path(problem_dir)
        self.output_dir = output_dir or (self.problem_dir / "tests")
        self.schema_validator = SchemaValidator()
        
        # Language adapters for reference solution execution
        self.adapters = {
            'python': PythonAdapter(),
            'cpp': CppAdapter(),
            'c': CppAdapter(),  # C uses same adapter as C++
        }
    
    def generate_tests(self, generator_type: str = "auto", num_cases: int = None, 
                      seed: int = 42, force: bool = False) -> Dict[str, Any]:
        """
        Generate test cases for the problem.
        
        Args:
            generator_type: Type of generator to use ("auto", "string", "simple", etc.)
            num_cases: Number of test cases to generate (overrides problem spec)
            seed: Random seed for generation
            force: Force regeneration even if tests exist
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Load problem specification
            problem = self._load_problem()
            
            # Check if tests already exist
            if not force and self._tests_exist():
                logger.info("Tests already exist. Use --force to regenerate.")
                return {"status": "skipped", "reason": "tests_exist"}
            
            # Get test specification
            test_spec = problem.get('test_spec', {})
            
            # Determine generator configuration
            config = self._create_generator_config(
                test_spec, generator_type, num_cases, seed
            )
            
            # Create generator
            generator = self._create_generator(generator_type, config, test_spec)
            
            # Generate test cases
            logger.info(f"Generating {config.num_cases} test cases using {generator.__class__.__name__}")
            test_cases = generator.generate_test_cases()
            
            # Create output directories
            self._create_output_directories()
            
            # Write test input files
            self._write_test_inputs(test_cases)
            
            # Execute reference solution to generate expected outputs
            reference_solution = self._find_reference_solution()
            if reference_solution:
                self._generate_expected_outputs(test_cases, reference_solution)
            else:
                logger.warning("No reference solution found. Only input files generated.")
            
            # Write generation metadata
            metadata = self._create_metadata(generator, test_cases, config)
            self._write_metadata(metadata)
            
            logger.info(f"Successfully generated {len(test_cases)} test cases")
            
            return {
                "status": "success",
                "num_cases": len(test_cases),
                "generator": generator.__class__.__name__,
                "output_dir": str(self.output_dir),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            raise TestGenerationError(f"Failed to generate tests: {e}")
    
    def _load_problem(self) -> Dict[str, Any]:
        """Load problem specification from problem.json."""
        problem_file = self.problem_dir / "problem.json"
        
        if not problem_file.exists():
            raise TestGenerationError(f"problem.json not found in {self.problem_dir}")
        
        try:
            with open(problem_file, 'r', encoding='utf-8') as f:
                problem = json.load(f)
            
            # Validate problem structure
            if 'slug' not in problem:
                raise TestGenerationError("problem.json missing required 'slug' field")
            
            return problem
            
        except json.JSONDecodeError as e:
            raise TestGenerationError(f"Invalid JSON in problem.json: {e}")
    
    def _tests_exist(self) -> bool:
        """Check if test files already exist."""
        if not self.output_dir.exists():
            return False
        
        # Check for any .in files (input files)
        input_files = list(self.output_dir.glob("*.in"))
        return len(input_files) > 0
    
    def _create_generator_config(self, test_spec: Dict[str, Any], 
                               generator_type: str, num_cases: Optional[int], 
                               seed: int) -> GeneratorConfig:
        """Create generator configuration from test spec."""
        # Get number of cases
        if num_cases is not None:
            total_cases = num_cases
        else:
            total_cases = test_spec.get('num_cases', 10)
        
        # Get case types
        case_types_spec = test_spec.get('case_types', ['unit'])
        case_types = []
        for case_type in case_types_spec:
            if case_type == 'unit':
                case_types.append(TestCaseType.UNIT)
            elif case_type == 'edge':
                case_types.append(TestCaseType.EDGE)
            elif case_type == 'stress':
                case_types.append(TestCaseType.STRESS)
            elif case_type == 'sample':
                case_types.append(TestCaseType.SAMPLE)
            elif case_type == 'hidden':
                case_types.append(TestCaseType.HIDDEN)
        
        if not case_types:
            case_types = [TestCaseType.UNIT]
        
        # Create base config
        if generator_type in ['string', 'cover_all_chars'] or 'string' in test_spec:
            # String generator config
            string_spec = test_spec.get('string', {})
            
            config = StringGeneratorConfig(
                seed=seed,
                num_cases=total_cases,
                case_types=case_types,
                constraints=test_spec.get('constraints', {}),
                problem_id=test_spec.get('problem_id'),
                min_length=string_spec.get('min_length', 1),
                max_length=string_spec.get('max_length', 20),
                charset=string_spec.get('charset', 'lowercase'),
                ensure_coverage=string_spec.get('ensure_coverage', False),
                word_list=string_spec.get('word_list')
            )
            
            # Parse patterns
            patterns_spec = string_spec.get('patterns', ['random'])
            patterns = []
            for pattern in patterns_spec:
                if pattern == 'random':
                    patterns.append(StringPattern.RANDOM)
                elif pattern == 'palindrome':
                    patterns.append(StringPattern.PALINDROME)
                elif pattern == 'repeated':
                    patterns.append(StringPattern.REPEATED)
                elif pattern == 'alternating':
                    patterns.append(StringPattern.ALTERNATING)
                elif pattern == 'ascending':
                    patterns.append(StringPattern.ASCENDING)
                elif pattern == 'descending':
                    patterns.append(StringPattern.DESCENDING)
                elif pattern == 'mixed_case':
                    patterns.append(StringPattern.MIXED_CASE)
                elif pattern == 'words':
                    patterns.append(StringPattern.WORDS)
                elif pattern == 'sentences':
                    patterns.append(StringPattern.SENTENCES)
            
            config.patterns = patterns if patterns else [StringPattern.RANDOM]
            return config
        else:
            # Simple generator config
            return GeneratorConfig(
                seed=seed,
                num_cases=total_cases,
                case_types=case_types,
                constraints=test_spec.get('constraints', {}),
                problem_id=test_spec.get('problem_id')
            )
    
    def _create_generator(self, generator_type: str, config: GeneratorConfig, 
                         test_spec: Dict[str, Any]):
        """Create the appropriate generator based on type and spec."""
        if generator_type == "auto":
            # Auto-detect generator type based on test_spec
            if 'string' in test_spec:
                generator_type = "string"
            else:
                generator_type = "simple"
        
        if generator_type == "string":
            return StringTestGenerator(config)
        elif generator_type == "cover_all_chars":
            return CoverAllCharsGenerator(config)
        elif generator_type == "reverse_string":
            return ReverseStringGenerator(config)
        elif generator_type == "uppercase":
            return UppercaseGenerator(config)
        elif generator_type == "lowercase":
            return LowercaseGenerator(config)
        elif generator_type == "palindrome_check":
            return PalindromeCheckGenerator(config)
        elif generator_type == "character_count":
            return CharacterCountGenerator(config)
        elif generator_type == "string_length":
            return StringLengthGenerator(config)
        elif generator_type == "simple":
            return SimpleTestGenerator(config)
        else:
            raise TestGenerationError(f"Unknown generator type: {generator_type}")
    
    def _create_output_directories(self):
        """Create output directories for test files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different test types
        (self.output_dir / "sample").mkdir(exist_ok=True)
        (self.output_dir / "unit").mkdir(exist_ok=True)
        (self.output_dir / "hidden").mkdir(exist_ok=True)
    
    def _write_test_inputs(self, test_cases: List):
        """Write test input files."""
        for i, test_case in enumerate(test_cases):
            case_num = i + 1
            case_type = test_case.case_type.value
            
            # Determine output directory based on case type
            if case_type == "sample":
                output_dir = self.output_dir / "sample"
            elif case_type in ["unit", "edge", "stress"]:
                output_dir = self.output_dir / "unit"
            else:
                output_dir = self.output_dir / "hidden"
            
            # Write input file
            input_file = output_dir / f"{case_num:02d}.in"
            
            # Format input data
            input_data = self._format_input_data(test_case.input_data)
            
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(input_data)
            
            logger.debug(f"Wrote input file: {input_file}")
    
    def _format_input_data(self, input_data: Any) -> str:
        """Format input data for writing to file."""
        if isinstance(input_data, str):
            return input_data + '\n'
        elif isinstance(input_data, (int, float)):
            return str(input_data) + '\n'
        elif isinstance(input_data, (list, tuple)):
            # Handle arrays/lists
            if len(input_data) == 1:
                return str(input_data[0]) + '\n'
            else:
                return '\n'.join(str(item) for item in input_data) + '\n'
        elif isinstance(input_data, dict):
            # Handle structured input
            lines = []
            for key, value in input_data.items():
                if isinstance(value, (list, tuple)):
                    lines.append(str(len(value)))
                    lines.extend(str(item) for item in value)
                else:
                    lines.append(str(value))
            return '\n'.join(lines) + '\n'
        else:
            return str(input_data) + '\n'
    
    def _find_reference_solution(self) -> Optional[Tuple[Path, str]]:
        """Find reference solution file and determine language."""
        # Look for reference solution files
        solution_patterns = [
            ("solution.py", "python"),
            ("reference.py", "python"),
            ("main.py", "python"),
            ("solution.cpp", "cpp"),
            ("reference.cpp", "cpp"),
            ("main.cpp", "cpp"),
            ("solution.c", "c"),
            ("reference.c", "c"),
            ("main.c", "c"),
        ]
        
        for filename, language in solution_patterns:
            solution_file = self.problem_dir / filename
            if solution_file.exists():
                return solution_file, language
        
        # Look in solutions directory
        solutions_dir = self.problem_dir / "solutions"
        if solutions_dir.exists():
            for filename, language in solution_patterns:
                solution_file = solutions_dir / filename
                if solution_file.exists():
                    return solution_file, language
        
        return None
    
    def _generate_expected_outputs(self, test_cases: List, 
                                 reference_solution: Tuple[Path, str]):
        """Generate expected output files by executing reference solution."""
        solution_file, language = reference_solution
        
        if language not in self.adapters:
            logger.warning(f"No adapter available for language: {language}")
            return
        
        adapter = self.adapters[language]
        
        logger.info(f"Executing reference solution: {solution_file}")
        
        # Compile if necessary
        if language in ['cpp', 'c']:
            try:
                compile_result = adapter.compile(solution_file)
                if not compile_result.success:
                    logger.error(f"Failed to compile reference solution: {compile_result.stderr}")
                    return
            except Exception as e:
                logger.error(f"Compilation error: {e}")
                return
        
        # Execute for each test case
        for i, test_case in enumerate(test_cases):
            case_num = i + 1
            case_type = test_case.case_type.value
            
            # Determine directories
            if case_type == "sample":
                input_dir = output_dir = self.output_dir / "sample"
            elif case_type in ["unit", "edge", "stress"]:
                input_dir = output_dir = self.output_dir / "unit"
            else:
                input_dir = output_dir = self.output_dir / "hidden"
            
            input_file = input_dir / f"{case_num:02d}.in"
            output_file = output_dir / f"{case_num:02d}.out"
            
            try:
                # Read input
                with open(input_file, 'r', encoding='utf-8') as f:
                    input_data = f.read()
                
                # Execute solution
                if language == 'python':
                    result = adapter.run(solution_file, input_data)
                else:
                    # For compiled languages, run the executable
                    executable = solution_file.with_suffix('.exe' if os.name == 'nt' else '')
                    result = adapter.run(executable, input_data)
                
                if result.success:
                    # Write expected output
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    
                    logger.debug(f"Generated expected output: {output_file}")
                else:
                    logger.error(f"Execution failed for test case {case_num}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error generating output for test case {case_num}: {e}")
    
    def _create_metadata(self, generator, test_cases: List, config: GeneratorConfig) -> Dict[str, Any]:
        """Create metadata about the generation process."""
        metadata = {
            "generator": {
                "type": generator.__class__.__name__,
                "config": {
                    "seed": config.seed,
                    "num_cases": config.num_cases,
                    "case_types": [ct.value for ct in config.case_types],
                    "constraints": config.constraints,
                    "problem_id": config.problem_id
                }
            },
            "test_cases": [
                {
                    "case_number": i + 1,
                    "type": tc.case_type.value,
                    "description": tc.description,
                    "metadata": tc.metadata
                }
                for i, tc in enumerate(test_cases)
            ],
            "generation_time": None,  # Could add timestamp
            "version": "1.0"
        }
        
        # Add string-specific metadata if applicable
        if hasattr(config, 'min_length'):
            metadata["generator"]["config"].update({
                "min_length": config.min_length,
                "max_length": config.max_length,
                "charset": config.charset,
                "patterns": [p.value for p in config.patterns] if hasattr(config, 'patterns') else None,
                "ensure_coverage": getattr(config, 'ensure_coverage', False)
            })
        
        # Add coverage report if available
        if hasattr(generator, 'get_coverage_report'):
            try:
                coverage_report = generator.get_coverage_report()
                metadata["coverage"] = coverage_report
            except:
                pass
        
        return metadata
    
    def _write_metadata(self, metadata: Dict[str, Any]):
        """Write generation metadata to file."""
        metadata_file = self.output_dir / "generation_metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Wrote metadata: {metadata_file}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test cases for coding problems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/problem                    # Auto-detect generator
  %(prog)s /path/to/problem --type string     # Use string generator
  %(prog)s /path/to/problem --num-cases 20    # Generate 20 test cases
  %(prog)s /path/to/problem --seed 123        # Use specific seed
  %(prog)s /path/to/problem --force           # Force regeneration
        """
    )
    
    parser.add_argument(
        'problem_dir',
        type=Path,
        help='Directory containing problem.json'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        help='Output directory for generated tests (default: problem_dir/tests)'
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=[
            'auto', 'simple', 'string', 'cover_all_chars',
            'reverse_string', 'uppercase', 'lowercase',
            'palindrome_check', 'character_count', 'string_length'
        ],
        default='auto',
        help='Type of generator to use (default: auto)'
    )
    
    parser.add_argument(
        '--num-cases', '-n',
        type=int,
        help='Number of test cases to generate (overrides problem spec)'
    )
    
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=42,
        help='Random seed for generation (default: 42)'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force regeneration even if tests exist'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress all output except errors'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create test generator
        test_gen = TestGenerator(args.problem_dir, args.output_dir)
        
        # Generate tests
        result = test_gen.generate_tests(
            generator_type=args.type,
            num_cases=args.num_cases,
            seed=args.seed,
            force=args.force
        )
        
        if result["status"] == "success":
            print(f"✓ Generated {result['num_cases']} test cases using {result['generator']}")
            print(f"  Output directory: {result['output_dir']}")
        elif result["status"] == "skipped":
            print("⚠ Test generation skipped:", result["reason"])
            sys.exit(1)
        
    except TestGenerationError as e:
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Test generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()