"""
Test result aggregation and analysis system.

This module provides comprehensive test result collection, analysis,
and reporting functionality for coding problem solutions.
"""

import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime, timezone
import statistics
import math

class TestStatus(Enum):
    """Individual test case status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    MEMORY_EXCEEDED = "MEMORY_EXCEEDED"
    SKIPPED = "SKIPPED"

class OverallStatus(Enum):
    """Overall test suite status."""
    ALL_PASSED = "ALL_PASSED"
    PARTIAL_PASSED = "PARTIAL_PASSED"
    ALL_FAILED = "ALL_FAILED"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

@dataclass
class TestCaseResult:
    """Individual test case result with detailed metrics."""
    test_id: str
    status: TestStatus
    input_data: str = ""
    expected_output: str = ""
    actual_output: str = ""
    error_message: str = ""
    execution_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    similarity_score: float = 0.0
    comparator_used: str = ""
    diff_details: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PerformanceMetrics:
    """Performance analysis metrics."""
    total_execution_time_ms: float
    average_execution_time_ms: float
    median_execution_time_ms: float
    max_execution_time_ms: float
    min_execution_time_ms: float
    total_memory_usage_mb: float
    average_memory_usage_mb: float
    peak_memory_usage_mb: float
    time_complexity_estimate: str = "Unknown"
    space_complexity_estimate: str = "Unknown"
    
    @classmethod
    def from_test_results(cls, results: List[TestCaseResult]) -> 'PerformanceMetrics':
        """Calculate performance metrics from test results."""
        if not results:
            return cls(0, 0, 0, 0, 0, 0, 0, 0)
        
        execution_times = [r.execution_time_ms for r in results if r.execution_time_ms > 0]
        memory_usages = [r.memory_usage_mb for r in results if r.memory_usage_mb > 0]
        
        total_time = sum(execution_times)
        avg_time = statistics.mean(execution_times) if execution_times else 0
        median_time = statistics.median(execution_times) if execution_times else 0
        max_time = max(execution_times) if execution_times else 0
        min_time = min(execution_times) if execution_times else 0
        
        total_memory = sum(memory_usages)
        avg_memory = statistics.mean(memory_usages) if memory_usages else 0
        peak_memory = max(memory_usages) if memory_usages else 0
        
        return cls(
            total_execution_time_ms=total_time,
            average_execution_time_ms=avg_time,
            median_execution_time_ms=median_time,
            max_execution_time_ms=max_time,
            min_execution_time_ms=min_time,
            total_memory_usage_mb=total_memory,
            average_memory_usage_mb=avg_memory,
            peak_memory_usage_mb=peak_memory
        )

@dataclass
class QualityMetrics:
    """Code quality and correctness metrics."""
    passed_tests: int
    failed_tests: int
    total_tests: int
    pass_rate: float
    average_similarity_score: float
    correctness_score: float  # Weighted score considering partial credit
    edge_case_coverage: float
    error_types: Dict[str, int]
    
    @classmethod
    def from_test_results(cls, results: List[TestCaseResult]) -> 'QualityMetrics':
        """Calculate quality metrics from test results."""
        if not results:
            return cls(0, 0, 0, 0.0, 0.0, 0.0, 0.0, {})
        
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        total = len(results)
        pass_rate = passed / total if total > 0 else 0.0
        
        # Calculate average similarity score (for partial credit)
        similarity_scores = [r.similarity_score for r in results]
        avg_similarity = statistics.mean(similarity_scores) if similarity_scores else 0.0
        
        # Correctness score considers both pass rate and similarity
        correctness_score = (pass_rate * 0.8) + (avg_similarity * 0.2)
        
        # Count error types
        error_types = {}
        for result in results:
            if result.status != TestStatus.PASSED:
                error_type = result.status.value
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Edge case coverage (simplified - based on test variety)
        edge_case_coverage = min(1.0, total / 10.0)  # Assume 10+ tests = good coverage
        
        return cls(
            passed_tests=passed,
            failed_tests=failed,
            total_tests=total,
            pass_rate=pass_rate,
            average_similarity_score=avg_similarity,
            correctness_score=correctness_score,
            edge_case_coverage=edge_case_coverage,
            error_types=error_types
        )

@dataclass
class TestResults:
    """Comprehensive test results with analysis and metrics."""
    execution_id: str
    problem_id: str
    language: str
    overall_status: OverallStatus
    test_cases: List[TestCaseResult]
    performance_metrics: PerformanceMetrics
    quality_metrics: QualityMetrics
    compilation_logs: str = ""
    runtime_logs: str = ""
    timestamp: datetime = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def from_execution_results(
        cls,
        execution_id: str,
        problem_id: str,
        language: str,
        test_case_results: List[TestCaseResult],
        compilation_logs: str = "",
        runtime_logs: str = "",
        duration_ms: float = 0.0,
        metadata: Dict[str, Any] = None
    ) -> 'TestResults':
        """Create TestResults from execution data."""
        
        # Determine overall status
        overall_status = cls._determine_overall_status(test_case_results)
        
        # Calculate metrics
        performance_metrics = PerformanceMetrics.from_test_results(test_case_results)
        quality_metrics = QualityMetrics.from_test_results(test_case_results)
        
        return cls(
            execution_id=execution_id,
            problem_id=problem_id,
            language=language,
            overall_status=overall_status,
            test_cases=test_case_results,
            performance_metrics=performance_metrics,
            quality_metrics=quality_metrics,
            compilation_logs=compilation_logs,
            runtime_logs=runtime_logs,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
    
    @staticmethod
    def _determine_overall_status(test_cases: List[TestCaseResult]) -> OverallStatus:
        """Determine overall status from individual test results."""
        if not test_cases:
            return OverallStatus.INTERNAL_ERROR
        
        # Check for compilation/system errors first
        error_statuses = [r.status for r in test_cases]
        
        if any(status == TestStatus.ERROR for status in error_statuses):
            return OverallStatus.RUNTIME_ERROR
        
        if any(status == TestStatus.TIMEOUT for status in error_statuses):
            return OverallStatus.TIMEOUT_ERROR
        
        if any(status == TestStatus.MEMORY_EXCEEDED for status in error_statuses):
            return OverallStatus.MEMORY_ERROR
        
        # Check pass/fail status
        passed_count = sum(1 for status in error_statuses if status == TestStatus.PASSED)
        total_count = len(test_cases)
        
        if passed_count == total_count:
            return OverallStatus.ALL_PASSED
        elif passed_count == 0:
            return OverallStatus.ALL_FAILED
        else:
            return OverallStatus.PARTIAL_PASSED
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a concise summary of the test results."""
        return {
            "execution_id": self.execution_id,
            "problem_id": self.problem_id,
            "language": self.language,
            "overall_status": self.overall_status.value,
            "passed_tests": self.quality_metrics.passed_tests,
            "total_tests": self.quality_metrics.total_tests,
            "pass_rate": f"{self.quality_metrics.pass_rate:.1%}",
            "correctness_score": f"{self.quality_metrics.correctness_score:.1%}",
            "total_time_ms": self.performance_metrics.total_execution_time_ms,
            "average_time_ms": self.performance_metrics.average_execution_time_ms,
            "peak_memory_mb": self.performance_metrics.peak_memory_usage_mb,
            "timestamp": self.timestamp.isoformat()
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Get a detailed analysis report."""
        return {
            "summary": self.get_summary(),
            "test_cases": [asdict(tc) for tc in self.test_cases],
            "performance": asdict(self.performance_metrics),
            "quality": asdict(self.quality_metrics),
            "logs": {
                "compilation": self.compilation_logs,
                "runtime": self.runtime_logs
            },
            "analysis": self._generate_analysis(),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_analysis(self) -> Dict[str, Any]:
        """Generate automated analysis of the results."""
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "patterns": [],
            "complexity_analysis": {}
        }
        
        # Analyze strengths
        if self.quality_metrics.pass_rate >= 0.8:
            analysis["strengths"].append("High test pass rate")
        
        if self.performance_metrics.average_execution_time_ms < 100:
            analysis["strengths"].append("Fast execution time")
        
        if self.quality_metrics.average_similarity_score >= 0.9:
            analysis["strengths"].append("High output accuracy")
        
        # Analyze weaknesses
        if self.quality_metrics.pass_rate < 0.5:
            analysis["weaknesses"].append("Low test pass rate - check algorithm logic")
        
        if self.performance_metrics.peak_memory_usage_mb > 256:
            analysis["weaknesses"].append("High memory usage - consider optimization")
        
        if self.performance_metrics.max_execution_time_ms > 1000:
            analysis["weaknesses"].append("Slow execution on some test cases")
        
        # Analyze patterns
        error_types = self.quality_metrics.error_types
        if error_types:
            most_common_error = max(error_types.items(), key=lambda x: x[1])
            analysis["patterns"].append(f"Most common issue: {most_common_error[0]} ({most_common_error[1]} cases)")
        
        # Time complexity estimation
        times = [tc.execution_time_ms for tc in self.test_cases if tc.execution_time_ms > 0]
        if len(times) >= 3:
            analysis["complexity_analysis"] = self._estimate_complexity(times)
        
        return analysis
    
    def _estimate_complexity(self, execution_times: List[float]) -> Dict[str, str]:
        """Estimate time complexity based on execution patterns."""
        if len(execution_times) < 3:
            return {"time_complexity": "Insufficient data"}
        
        # Simple heuristic based on time growth
        time_ratios = []
        for i in range(1, len(execution_times)):
            if execution_times[i-1] > 0:
                ratio = execution_times[i] / execution_times[i-1]
                time_ratios.append(ratio)
        
        if not time_ratios:
            return {"time_complexity": "Unable to determine"}
        
        avg_ratio = statistics.mean(time_ratios)
        
        if avg_ratio < 1.2:
            complexity = "O(1) or O(log n)"
        elif avg_ratio < 2.0:
            complexity = "O(n) or O(n log n)"
        elif avg_ratio < 4.0:
            complexity = "O(n²)"
        else:
            complexity = "O(n³) or higher"
        
        return {
            "time_complexity": complexity,
            "confidence": "Low" if len(time_ratios) < 5 else "Medium"
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Performance recommendations
        if self.performance_metrics.average_execution_time_ms > 500:
            recommendations.append("Consider optimizing algorithm for better time complexity")
        
        if self.performance_metrics.peak_memory_usage_mb > 128:
            recommendations.append("Review memory usage - consider more efficient data structures")
        
        # Quality recommendations
        if self.quality_metrics.pass_rate < 0.8:
            recommendations.append("Review failing test cases to identify logic errors")
        
        if self.quality_metrics.average_similarity_score < 0.7:
            recommendations.append("Check output formatting - results are close but not exact")
        
        # Error-specific recommendations
        error_types = self.quality_metrics.error_types
        if "TIMEOUT" in error_types:
            recommendations.append("Optimize algorithm to avoid timeout on large inputs")
        
        if "MEMORY_EXCEEDED" in error_types:
            recommendations.append("Reduce memory usage with more efficient algorithms")
        
        if "ERROR" in error_types:
            recommendations.append("Fix runtime errors - check for null pointers, array bounds, etc.")
        
        return recommendations
    
    def to_json(self) -> str:
        """Serialize results to JSON."""
        data = asdict(self)
        # Convert datetime to ISO string
        data['timestamp'] = self.timestamp.isoformat()
        # Convert enums to strings
        data['overall_status'] = self.overall_status.value
        for tc in data['test_cases']:
            tc['status'] = tc['status'].value if hasattr(tc['status'], 'value') else tc['status']
        
        return json.dumps(data, indent=2, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TestResults':
        """Deserialize results from JSON."""
        data = json.loads(json_str)
        
        # Convert timestamp back
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert enum strings back to enums
        data['overall_status'] = OverallStatus(data['overall_status'])
        
        # Convert test case data
        test_cases = []
        for tc_data in data['test_cases']:
            tc_data['status'] = TestStatus(tc_data['status'])
            test_cases.append(TestCaseResult(**tc_data))
        data['test_cases'] = test_cases
        
        # Convert metrics
        data['performance_metrics'] = PerformanceMetrics(**data['performance_metrics'])
        data['quality_metrics'] = QualityMetrics(**data['quality_metrics'])
        
        return cls(**data)

class ResultsAggregator:
    """Aggregates and analyzes multiple test results."""
    
    def __init__(self):
        self.results_history: List[TestResults] = []
    
    def add_result(self, result: TestResults):
        """Add a test result to the aggregator."""
        self.results_history.append(result)
    
    def get_problem_statistics(self, problem_id: str) -> Dict[str, Any]:
        """Get statistics for a specific problem."""
        problem_results = [r for r in self.results_history if r.problem_id == problem_id]
        
        if not problem_results:
            return {"error": "No results found for problem"}
        
        return {
            "problem_id": problem_id,
            "total_attempts": len(problem_results),
            "success_rate": sum(1 for r in problem_results if r.overall_status == OverallStatus.ALL_PASSED) / len(problem_results),
            "average_pass_rate": statistics.mean([r.quality_metrics.pass_rate for r in problem_results]),
            "best_time": min([r.performance_metrics.average_execution_time_ms for r in problem_results]),
            "languages_used": list(set([r.language for r in problem_results])),
            "common_errors": self._get_common_errors(problem_results),
            "improvement_trend": self._calculate_improvement_trend(problem_results)
        }
    
    def get_language_statistics(self, language: str) -> Dict[str, Any]:
        """Get statistics for a specific language."""
        lang_results = [r for r in self.results_history if r.language == language]
        
        if not lang_results:
            return {"error": "No results found for language"}
        
        return {
            "language": language,
            "total_attempts": len(lang_results),
            "average_success_rate": statistics.mean([1 if r.overall_status == OverallStatus.ALL_PASSED else 0 for r in lang_results]),
            "average_execution_time": statistics.mean([r.performance_metrics.average_execution_time_ms for r in lang_results]),
            "problems_solved": len(set([r.problem_id for r in lang_results if r.overall_status == OverallStatus.ALL_PASSED])),
            "common_issues": self._get_common_errors(lang_results)
        }
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall statistics across all results."""
        if not self.results_history:
            return {"error": "No results available"}
        
        return {
            "total_attempts": len(self.results_history),
            "unique_problems": len(set([r.problem_id for r in self.results_history])),
            "languages_used": len(set([r.language for r in self.results_history])),
            "overall_success_rate": sum(1 for r in self.results_history if r.overall_status == OverallStatus.ALL_PASSED) / len(self.results_history),
            "average_execution_time": statistics.mean([r.performance_metrics.average_execution_time_ms for r in self.results_history]),
            "most_common_language": max(set([r.language for r in self.results_history]), key=lambda x: sum(1 for r in self.results_history if r.language == x)),
            "performance_trend": self._calculate_performance_trend(),
            "recent_activity": self._get_recent_activity()
        }
    
    def _get_common_errors(self, results: List[TestResults]) -> Dict[str, int]:
        """Get common error types across results."""
        error_counts = {}
        for result in results:
            for error_type, count in result.quality_metrics.error_types.items():
                error_counts[error_type] = error_counts.get(error_type, 0) + count
        
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _calculate_improvement_trend(self, results: List[TestResults]) -> str:
        """Calculate improvement trend for a problem."""
        if len(results) < 2:
            return "Insufficient data"
        
        # Sort by timestamp
        sorted_results = sorted(results, key=lambda x: x.timestamp)
        recent_results = sorted_results[-3:]  # Last 3 attempts
        older_results = sorted_results[:-3] if len(sorted_results) > 3 else sorted_results[:1]
        
        recent_avg = statistics.mean([r.quality_metrics.pass_rate for r in recent_results])
        older_avg = statistics.mean([r.quality_metrics.pass_rate for r in older_results])
        
        if recent_avg > older_avg + 0.1:
            return "Improving"
        elif recent_avg < older_avg - 0.1:
            return "Declining"
        else:
            return "Stable"
    
    def _calculate_performance_trend(self) -> str:
        """Calculate overall performance trend."""
        if len(self.results_history) < 5:
            return "Insufficient data"
        
        # Sort by timestamp and compare recent vs older performance
        sorted_results = sorted(self.results_history, key=lambda x: x.timestamp)
        recent = sorted_results[-10:]  # Last 10 attempts
        older = sorted_results[:-10] if len(sorted_results) > 10 else sorted_results[:5]
        
        recent_success = sum(1 for r in recent if r.overall_status == OverallStatus.ALL_PASSED) / len(recent)
        older_success = sum(1 for r in older if r.overall_status == OverallStatus.ALL_PASSED) / len(older)
        
        if recent_success > older_success + 0.1:
            return "Improving"
        elif recent_success < older_success - 0.1:
            return "Declining"
        else:
            return "Stable"
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent activity summary."""
        recent_results = sorted(self.results_history, key=lambda x: x.timestamp, reverse=True)[:5]
        
        return [
            {
                "problem_id": r.problem_id,
                "language": r.language,
                "status": r.overall_status.value,
                "pass_rate": f"{r.quality_metrics.pass_rate:.1%}",
                "timestamp": r.timestamp.isoformat()
            }
            for r in recent_results
        ]