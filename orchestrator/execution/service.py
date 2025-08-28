import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .executor import CodeExecutor, TestCase, ExecutionStatus, TestCaseResult
from ..db.progress import ProgressTracker
from ..utils.limits import ResourceLimits
from ..testing.results import (
    TestResults, 
    TestCaseResult as ResultsTestCase, 
    TestStatus, 
    OverallStatus,
    ResultsAggregator
)

logger = logging.getLogger(__name__)

class ExecutionService:
    """High-level service for managing code execution requests."""
    
    def __init__(self, work_dir: str = "/tmp/code_execution"):
        self.executor = CodeExecutor(work_dir)
        self.progress_tracker = ProgressTracker()
        self.resource_limits = ResourceLimits()
        self.results_aggregator = ResultsAggregator()
        
        # Execution statistics
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "avg_execution_time": 0.0,
        }
    
    async def execute_solution(
        self,
        code: str,
        language: str,
        problem_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a solution and return comprehensive results."""
        
        try:
            # Load problem test cases
            test_cases = await self._load_test_cases(problem_id)
            if not test_cases:
                return {
                    "status": "error",
                    "message": f"No test cases found for problem {problem_id}",
                    "results": []
                }
            
            # Check resource limits
            if not await self.resource_limits.check_execution_allowed(user_id):
                return {
                    "status": "error",
                    "message": "Rate limit exceeded. Please wait before submitting again.",
                    "results": []
                }
            
            # Track execution start
            execution_id = await self.progress_tracker.start_execution(
                user_id=user_id,
                session_id=session_id,
                problem_id=problem_id,
                language=language
            )
            
            # Execute code
            overall_status, test_results, logs = await self.executor.execute_code(
                code=code,
                language=language,
                test_cases=test_cases,
                problem_id=problem_id
            )
            
            # Convert to results format
            results_test_cases = []
            for test_result in test_results:
                status_mapping = {
                    ExecutionStatus.OK: TestStatus.PASSED,
                    ExecutionStatus.WA: TestStatus.FAILED,
                    ExecutionStatus.TLE: TestStatus.TIMEOUT,
                    ExecutionStatus.MLE: TestStatus.MEMORY_EXCEEDED,
                    ExecutionStatus.RE: TestStatus.ERROR,
                    ExecutionStatus.CE: TestStatus.ERROR,
                    ExecutionStatus.IE: TestStatus.ERROR
                }
                
                results_test_cases.append(ResultsTestCase(
                    test_id=test_result.test_case.id,
                    status=status_mapping.get(test_result.result.status, TestStatus.ERROR),
                    input_data=test_result.test_case.input_data,
                    expected_output=test_result.test_case.expected_output,
                    actual_output=test_result.result.output,
                    error_message=test_result.result.error,
                    execution_time_ms=test_result.result.time_ms,
                    memory_usage_mb=test_result.result.memory_mb,
                    similarity_score=getattr(test_result.result, 'similarity_score', 0.0),
                    comparator_used=getattr(test_result, 'comparator_used', 'Unknown'),
                    diff_details=test_result.diff
                ))
            
            # Create comprehensive test results
            test_results_obj = TestResults.from_execution_results(
                execution_id=execution_id,
                problem_id=problem_id,
                language=language,
                test_case_results=results_test_cases,
                compilation_logs=logs.get("compile", ""),
                runtime_logs=logs.get("stderr", ""),
                duration_ms=sum(tc.execution_time_ms for tc in results_test_cases)
            )
            
            # Add to aggregator for analytics
            self.results_aggregator.add_result(test_results_obj)
            
            # Process results for API response
            api_results = await self._process_results_for_api(
                overall_status, test_results, logs, execution_id
            )
            
            # Update statistics
            await self._update_stats(overall_status, api_results)
            
            # Track execution completion
            await self.progress_tracker.complete_execution(
                execution_id=execution_id,
                status=overall_status.value,
                results=api_results
            )
            
            # Add detailed results to API response
            api_results["detailed_analysis"] = test_results_obj.get_detailed_report()
            api_results["summary"] = test_results_obj.get_summary()
            
            return api_results
            
        except Exception as e:
            logger.error(f"Execution service error: {e}")
            return {
                "status": "error",
                "message": f"Internal execution error: {str(e)}",
                "results": []
            }
    
    async def validate_syntax(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Validate code syntax without execution."""
        
        try:
            is_valid, message = await self.executor.validate_code_syntax(code, language)
            
            return {
                "valid": is_valid,
                "message": message,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Syntax validation error: {e}")
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}",
                "language": language
            }
    
    async def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        basic_stats = {
            **self.stats,
            "resource_limits": await self.resource_limits.get_current_limits(),
            "active_executions": await self.progress_tracker.get_active_executions_count()
        }
        
        # Add aggregated analytics
        overall_analytics = self.results_aggregator.get_overall_statistics()
        if "error" not in overall_analytics:
            basic_stats.update(overall_analytics)
        
        return basic_stats
    
    async def get_problem_analytics(self, problem_id: str) -> Dict[str, Any]:
        """Get analytics for a specific problem."""
        return self.results_aggregator.get_problem_statistics(problem_id)
    
    async def get_language_analytics(self, language: str) -> Dict[str, Any]:
        """Get analytics for a specific language."""
        return self.results_aggregator.get_language_statistics(language)
    
    async def get_detailed_results(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results for a specific execution."""
        # Find the result in aggregator
        for result in self.results_aggregator.results_history:
            if result.execution_id == execution_id:
                return result.get_detailed_report()
        return None
    
    async def _load_test_cases(self, problem_id: str) -> List[TestCase]:
        """Load test cases for a problem."""
        try:
            # Load from problems directory
            problem_dir = Path(f"problems/{problem_id}")
            test_cases_file = problem_dir / "test_cases.json"
            
            if not test_cases_file.exists():
                # Fallback to default test cases
                return await self._get_default_test_cases(problem_id)
            
            with open(test_cases_file, 'r') as f:
                data = json.load(f)
            
            test_cases = []
            for i, case in enumerate(data.get("test_cases", [])):
                test_cases.append(TestCase(
                    id=f"test_{i+1}",
                    input_data=case.get("input", ""),
                    expected_output=case.get("output", ""),
                    time_limit=case.get("time_limit", 1.0),
                    memory_limit=case.get("memory_limit", 256),
                    comparison_type=case.get("comparison_type", "auto"),
                    comparison_config=case.get("comparison_config", {})
                ))
            
            return test_cases
            
        except Exception as e:
            logger.error(f"Error loading test cases for {problem_id}: {e}")
            return await self._get_default_test_cases(problem_id)
    
    async def _get_default_test_cases(self, problem_id: str) -> List[TestCase]:
        """Get default test cases for common problems."""
        
        default_cases = {
            "two-sum": [
                TestCase(
                    id="test_1",
                    input_data="[2,7,11,15]\n9",
                    expected_output="[0,1]",
                    time_limit=1.0,
                    comparison_type="array",
                    comparison_config={"ignore_order": False}
                ),
                TestCase(
                    id="test_2", 
                    input_data="[3,2,4]\n6",
                    expected_output="[1,2]",
                    time_limit=1.0,
                    comparison_type="array",
                    comparison_config={"ignore_order": False}
                )
            ],
            "add-two-numbers": [
                TestCase(
                    id="test_1",
                    input_data="[2,4,3]\n[5,6,4]",
                    expected_output="[7,0,8]",
                    time_limit=1.0
                )
            ],
            "longest-substring": [
                TestCase(
                    id="test_1",
                    input_data="abcabcbb",
                    expected_output="3",
                    time_limit=1.0
                ),
                TestCase(
                    id="test_2",
                    input_data="bbbbb", 
                    expected_output="1",
                    time_limit=1.0
                )
            ],
            "median-sorted-arrays": [
                TestCase(
                    id="test_1",
                    input_data="[1,3]\n[2]",
                    expected_output="2.0",
                    time_limit=1.0
                )
            ],
            "valid-parentheses": [
                TestCase(
                    id="test_1",
                    input_data="()",
                    expected_output="true",
                    time_limit=1.0,
                    comparison_type="exact",
                    comparison_config={"case_sensitive": False}
                ),
                TestCase(
                    id="test_2",
                    input_data="()[]{}",
                    expected_output="true",
                    time_limit=1.0,
                    comparison_type="exact",
                    comparison_config={"case_sensitive": False}
                ),
                TestCase(
                    id="test_3",
                    input_data="(]",
                    expected_output="false",
                    time_limit=1.0,
                    comparison_type="exact",
                    comparison_config={"case_sensitive": False}
                )
            ]
        }
        
        return default_cases.get(problem_id, [
            TestCase(
                id="test_1",
                input_data="",
                expected_output="",
                time_limit=1.0
            )
        ])
    
    async def _process_results_for_api(
        self,
        overall_status: ExecutionStatus,
        test_results: List[TestCaseResult],
        logs: Dict[str, str],
        execution_id: str
    ) -> Dict[str, Any]:
        """Process execution results into API response format."""
        
        # Calculate statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.result.status == ExecutionStatus.OK)
        total_time = sum(r.result.time_ms for r in test_results)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        
        # Format test case results
        formatted_results = []
        for result in test_results:
            formatted_results.append({
                "test_id": result.test_case.id,
                "status": result.result.status.value,
                "input": result.test_case.input_data,
                "expected_output": result.test_case.expected_output,
                "actual_output": result.result.output,
                "error": result.result.error,
                "time_ms": result.result.time_ms,
                "memory_mb": result.result.memory_mb,
                "diff": result.diff,
                "passed": result.result.status == ExecutionStatus.OK
            })
        
        # Determine overall result
        if overall_status == ExecutionStatus.OK:
            status = "accepted" if passed_tests == total_tests else "wrong_answer"
        elif overall_status == ExecutionStatus.CE:
            status = "compilation_error"
        elif overall_status == ExecutionStatus.TLE:
            status = "time_limit_exceeded"
        elif overall_status == ExecutionStatus.MLE:
            status = "memory_limit_exceeded"
        elif overall_status == ExecutionStatus.RE:
            status = "runtime_error"
        else:
            status = "internal_error"
        
        return {
            "execution_id": execution_id,
            "status": status,
            "overall_result": overall_status.value,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_time_ms": total_time,
            "average_time_ms": avg_time,
            "test_results": formatted_results,
            "logs": logs,
            "message": self._get_status_message(overall_status, passed_tests, total_tests)
        }
    
    def _get_status_message(
        self,
        status: ExecutionStatus,
        passed: int,
        total: int
    ) -> str:
        """Get human-readable status message."""
        
        if status == ExecutionStatus.OK:
            if passed == total:
                return f"All {total} test cases passed! ✅"
            else:
                return f"{passed}/{total} test cases passed"
        elif status == ExecutionStatus.CE:
            return "Compilation failed. Please check your syntax."
        elif status == ExecutionStatus.TLE:
            return "Time limit exceeded. Your solution is too slow."
        elif status == ExecutionStatus.MLE:
            return "Memory limit exceeded. Your solution uses too much memory."
        elif status == ExecutionStatus.RE:
            return "Runtime error occurred during execution."
        elif status == ExecutionStatus.WA:
            return f"{passed}/{total} test cases passed. Check your logic."
        else:
            return "Internal error occurred during execution."
    
    async def _update_stats(self, status: ExecutionStatus, results: Dict[str, Any]):
        """Update execution statistics."""
        self.stats["total_executions"] += 1
        
        if status == ExecutionStatus.OK:
            self.stats["successful_executions"] += 1
        else:
            self.stats["failed_executions"] += 1
        
        # Update average execution time
        total_time = results.get("total_time_ms", 0)
        current_avg = self.stats["avg_execution_time"]
        total_execs = self.stats["total_executions"]
        
        self.stats["avg_execution_time"] = (
            (current_avg * (total_execs - 1) + total_time) / total_execs
        )

# Global execution service instance
execution_service = ExecutionService()