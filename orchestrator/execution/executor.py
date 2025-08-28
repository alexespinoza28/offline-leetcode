import asyncio
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import subprocess
import shutil
import resource
import signal
from dataclasses import dataclass
from enum import Enum

class ExecutionStatus(Enum):
    OK = "OK"
    WA = "WA"  # Wrong Answer
    TLE = "TLE"  # Time Limit Exceeded
    MLE = "MLE"  # Memory Limit Exceeded
    RE = "RE"  # Runtime Error
    CE = "CE"  # Compilation Error
    IE = "IE"  # Internal Error

@dataclass
class TestCase:
    id: str
    input_data: str
    expected_output: str
    time_limit: float = 1.0
    memory_limit: int = 256  # MB
    comparison_type: str = "auto"  # auto, exact, numeric, json, array
    comparison_config: dict = None  # Additional comparator configuration

@dataclass
class ExecutionResult:
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    time_ms: float = 0.0
    memory_mb: float = 0.0
    exit_code: int = 0
    similarity_score: float = 0.0

@dataclass
class TestCaseResult:
    test_case: TestCase
    result: ExecutionResult
    diff: Optional[str] = None

class CodeExecutor:
    """Secure code execution engine with resource limits and sandboxing."""
    
    def __init__(self, work_dir: str = "/tmp/code_execution"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True, parents=True)
        
        # Language configurations
        self.language_configs = {
            "py": {
                "extension": ".py",
                "compile_cmd": None,
                "run_cmd": ["python3", "{file}"],
                "timeout": 10.0,
                "memory_limit": 256,  # MB
            },
            "cpp": {
                "extension": ".cpp",
                "compile_cmd": ["g++", "-std=c++17", "-O2", "-o", "{executable}", "{file}"],
                "run_cmd": ["./{executable}"],
                "timeout": 10.0,
                "memory_limit": 256,
            },
            "c": {
                "extension": ".c",
                "compile_cmd": ["gcc", "-std=c11", "-O2", "-o", "{executable}", "{file}"],
                "run_cmd": ["./{executable}"],
                "timeout": 10.0,
                "memory_limit": 256,
            },
            "js": {
                "extension": ".js",
                "compile_cmd": None,
                "run_cmd": ["node", "{file}"],
                "timeout": 10.0,
                "memory_limit": 256,
            },
            "java": {
                "extension": ".java",
                "compile_cmd": ["javac", "{file}"],
                "run_cmd": ["java", "{class_name}"],
                "timeout": 15.0,
                "memory_limit": 512,
            },
        }
    
    async def execute_code(
        self,
        code: str,
        language: str,
        test_cases: List[TestCase],
        problem_id: str = None
    ) -> Tuple[ExecutionStatus, List[TestCaseResult], Dict[str, str]]:
        """Execute code against test cases and return results."""
        
        if language not in self.language_configs:
            return ExecutionStatus.IE, [], {"error": f"Unsupported language: {language}"}
        
        # Create unique execution directory
        execution_id = str(uuid.uuid4())
        exec_dir = self.work_dir / execution_id
        exec_dir.mkdir(exist_ok=True)
        
        try:
            # Prepare code file
            config = self.language_configs[language]
            code_file = exec_dir / f"solution{config['extension']}"
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Compile if necessary
            compile_logs = ""
            if config["compile_cmd"]:
                compile_result = await self._compile_code(code_file, config, exec_dir)
                if compile_result.status != ExecutionStatus.OK:
                    return compile_result.status, [], {
                        "compile": compile_result.error,
                        "stderr": compile_result.error
                    }
                compile_logs = compile_result.output
            
            # Run test cases
            test_results = []
            overall_status = ExecutionStatus.OK
            
            for test_case in test_cases:
                result = await self._run_test_case(code_file, config, exec_dir, test_case)
                
                # Compare output using appropriate comparator
                diff = None
                if result.result.status == ExecutionStatus.OK:
                    expected = test_case.expected_output.strip()
                    actual = result.result.output.strip()
                    
                    # Use advanced comparison
                    comparison_result = self._compare_outputs(
                        expected, actual, test_case.comparison_type, test_case.comparison_config
                    )
                    
                    if not comparison_result["match"]:
                        result.result.status = ExecutionStatus.WA
                        diff = comparison_result["diff"]
                        overall_status = ExecutionStatus.WA
                    else:
                        # Store similarity score for analytics
                        result.result.similarity_score = comparison_result.get("similarity", 1.0)
                
                result.diff = diff
                test_results.append(result)
                
                # Update overall status
                if result.result.status != ExecutionStatus.OK and overall_status == ExecutionStatus.OK:
                    overall_status = result.result.status
            
            logs = {"compile": compile_logs}
            if any(r.result.error for r in test_results):
                logs["stderr"] = "\n".join(r.result.error for r in test_results if r.result.error)
            
            return overall_status, test_results, logs
            
        except Exception as e:
            return ExecutionStatus.IE, [], {"error": f"Internal execution error: {str(e)}"}
        
        finally:
            # Cleanup
            try:
                shutil.rmtree(exec_dir)
            except Exception as e:
                print(f"Warning: Failed to cleanup {exec_dir}: {e}")
    
    async def _compile_code(
        self, 
        code_file: Path, 
        config: Dict, 
        exec_dir: Path
    ) -> ExecutionResult:
        """Compile code if compilation is required."""
        
        executable = exec_dir / "solution"
        class_name = "Main" if config["extension"] == ".java" else "solution"
        
        cmd = []
        for part in config["compile_cmd"]:
            cmd.append(part.format(
                file=str(code_file),
                executable=str(executable),
                class_name=class_name
            ))
        
        try:
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=exec_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024  # 1MB limit for compilation output
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=30.0  # 30 second compile timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ExecutionResult(
                    status=ExecutionStatus.CE,
                    error="Compilation timeout",
                    time_ms=(time.time() - start_time) * 1000
                )
            
            compile_time = (time.time() - start_time) * 1000
            
            if process.returncode != 0:
                return ExecutionResult(
                    status=ExecutionStatus.CE,
                    error=stderr.decode('utf-8', errors='replace'),
                    output=stdout.decode('utf-8', errors='replace'),
                    time_ms=compile_time,
                    exit_code=process.returncode
                )
            
            return ExecutionResult(
                status=ExecutionStatus.OK,
                output=stdout.decode('utf-8', errors='replace'),
                time_ms=compile_time
            )
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.IE,
                error=f"Compilation error: {str(e)}"
            )
    
    async def _run_test_case(
        self, 
        code_file: Path, 
        config: Dict, 
        exec_dir: Path, 
        test_case: TestCase
    ) -> TestCaseResult:
        """Run a single test case."""
        
        executable = exec_dir / "solution"
        class_name = "Main" if config["extension"] == ".java" else "solution"
        
        cmd = []
        for part in config["run_cmd"]:
            cmd.append(part.format(
                file=str(code_file),
                executable=str(executable),
                class_name=class_name
            ))
        
        try:
            start_time = time.time()
            
            # Create process with resource limits
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=exec_dir,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024 * 1024,  # 1MB output limit
                preexec_fn=self._set_resource_limits if os.name != 'nt' else None
            )
            
            try:
                # Send input and wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=test_case.input_data.encode('utf-8')),
                    timeout=test_case.time_limit
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                result = ExecutionResult(
                    status=ExecutionStatus.OK if process.returncode == 0 else ExecutionStatus.RE,
                    output=stdout.decode('utf-8', errors='replace'),
                    error=stderr.decode('utf-8', errors='replace'),
                    time_ms=execution_time,
                    exit_code=process.returncode
                )
                
                # Check for runtime error
                if process.returncode != 0:
                    result.status = ExecutionStatus.RE
                
                return TestCaseResult(test_case=test_case, result=result)
                
            except asyncio.TimeoutError:
                process.kill()
                try:
                    await process.wait()
                except:
                    pass
                
                return TestCaseResult(
                    test_case=test_case,
                    result=ExecutionResult(
                        status=ExecutionStatus.TLE,
                        error=f"Time limit exceeded ({test_case.time_limit}s)",
                        time_ms=test_case.time_limit * 1000
                    )
                )
                
        except Exception as e:
            return TestCaseResult(
                test_case=test_case,
                result=ExecutionResult(
                    status=ExecutionStatus.IE,
                    error=f"Execution error: {str(e)}"
                )
            )
    
    def _set_resource_limits(self):
        """Set resource limits for the child process (Unix only)."""
        try:
            # Set memory limit (in bytes)
            memory_limit = 256 * 1024 * 1024  # 256MB
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
            
            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))  # 10 seconds
            
            # Limit number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
            
            # Limit file size
            resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))  # 10MB
            
        except Exception as e:
            print(f"Warning: Could not set resource limits: {e}")
    
    def _generate_diff(self, expected: str, actual: str, comparison_type: str = "auto") -> str:
        """Generate a detailed diff using the appropriate comparator."""
        try:
            # Import here to avoid circular imports
            from ..testing.comparators import ComparatorFactory
            
            if comparison_type == "auto":
                comparator = ComparatorFactory.auto_detect_comparator(expected, actual)
            else:
                comparator = ComparatorFactory.create_comparator(comparison_type)
            
            comparison_result = comparator.compare(expected, actual)
            
            if comparison_result.diff:
                return comparison_result.diff
            else:
                return f"Outputs differ (similarity: {comparison_result.similarity_score:.1%})"
                
        except Exception as e:
            # Fallback to simple diff if comparator fails
            return self._simple_diff(expected, actual)
    
    def _simple_diff(self, expected: str, actual: str) -> str:
        """Generate a simple line-by-line diff as fallback."""
        expected_lines = expected.split('\n')
        actual_lines = actual.split('\n')
        
        diff_lines = []
        max_lines = max(len(expected_lines), len(actual_lines))
        
        for i in range(max_lines):
            exp_line = expected_lines[i] if i < len(expected_lines) else ""
            act_line = actual_lines[i] if i < len(actual_lines) else ""
            
            if exp_line != act_line:
                diff_lines.append(f"Line {i+1}:")
                diff_lines.append(f"  Expected: {repr(exp_line)}")
                diff_lines.append(f"  Actual:   {repr(act_line)}")
        
        return '\n'.join(diff_lines) if diff_lines else "No differences found"
    
    def _compare_outputs(self, expected: str, actual: str, comparison_type: str = "auto", config: dict = None) -> dict:
        """Compare outputs using the specified comparison method."""
        try:
            from ..testing.comparators import ComparatorFactory, ComparisonResult
            
            # Create comparator with configuration
            if comparison_type == "auto":
                comparator = ComparatorFactory.auto_detect_comparator(expected, actual)
            else:
                comparator_config = config or {}
                comparator = ComparatorFactory.create_comparator(comparison_type, **comparator_config)
            
            # Perform comparison
            result = comparator.compare(expected, actual)
            
            return {
                "match": result.result == ComparisonResult.MATCH,
                "diff": result.diff or result.message,
                "similarity": result.similarity_score,
                "comparator": comparator.get_name(),
                "message": result.message
            }
            
        except Exception as e:
            # Fallback to simple string comparison
            match = expected.strip() == actual.strip()
            diff = self._simple_diff(expected, actual) if not match else None
            
            return {
                "match": match,
                "diff": diff,
                "similarity": 1.0 if match else 0.0,
                "comparator": "Simple",
                "message": f"Fallback comparison (error: {str(e)})"
            }

    async def validate_code_syntax(self, code: str, language: str) -> Tuple[bool, str]:
        """Validate code syntax without execution."""
        if language not in self.language_configs:
            return False, f"Unsupported language: {language}"
        
        execution_id = str(uuid.uuid4())
        exec_dir = self.work_dir / execution_id
        exec_dir.mkdir(exist_ok=True)
        
        try:
            config = self.language_configs[language]
            code_file = exec_dir / f"syntax_check{config['extension']}"
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            if language == "py":
                # Python syntax check
                try:
                    compile(code, '<string>', 'exec')
                    return True, "Syntax is valid"
                except SyntaxError as e:
                    return False, f"Syntax error: {e}"
            
            elif language in ["cpp", "c"]:
                # Compile with syntax check only
                cmd = config["compile_cmd"].copy()
                cmd.append("-fsyntax-only")  # Only check syntax
                
                formatted_cmd = []
                for part in cmd:
                    formatted_cmd.append(part.format(
                        file=str(code_file),
                        executable="dummy"
                    ))
                
                process = await asyncio.create_subprocess_exec(
                    *formatted_cmd,
                    cwd=exec_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=10.0
                )
                
                if process.returncode == 0:
                    return True, "Syntax is valid"
                else:
                    return False, stderr.decode('utf-8', errors='replace')
            
            elif language == "js":
                # Node.js syntax check
                process = await asyncio.create_subprocess_exec(
                    "node", "--check", str(code_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=5.0
                )
                
                if process.returncode == 0:
                    return True, "Syntax is valid"
                else:
                    return False, stderr.decode('utf-8', errors='replace')
            
            elif language == "java":
                # Java compilation check
                compile_result = await self._compile_code(code_file, config, exec_dir)
                return compile_result.status == ExecutionStatus.OK, compile_result.error or "Syntax is valid"
            
            return True, "Syntax validation not implemented for this language"
            
        except Exception as e:
            return False, f"Syntax validation error: {str(e)}"
        
        finally:
            try:
                shutil.rmtree(exec_dir)
            except Exception:
                pass