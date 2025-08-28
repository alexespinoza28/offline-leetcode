import pytest
import json
from datetime import datetime, timezone
from orchestrator.testing.results import (
    TestCaseResult,
    TestResults,
    TestStatus,
    OverallStatus,
    PerformanceMetrics,
    QualityMetrics,
    ResultsAggregator
)

class TestTestCaseResult:
    """Test cases for TestCaseResult."""
    
    def test_basic_creation(self):
        """Test basic test case result creation."""
        result = TestCaseResult(
            test_id="test_1",
            status=TestStatus.PASSED,
            input_data="input",
            expected_output="expected",
            actual_output="actual",
            execution_time_ms=50.0,
            memory_usage_mb=10.0,
            similarity_score=1.0
        )
        
        assert result.test_id == "test_1"
        assert result.status == TestStatus.PASSED
        assert result.similarity_score == 1.0
        assert result.metadata == {}
    
    def test_with_metadata(self):
        """Test test case result with metadata."""
        metadata = {"comparator": "exact", "difficulty": "easy"}
        result = TestCaseResult(
            test_id="test_1",
            status=TestStatus.FAILED,
            metadata=metadata
        )
        
        assert result.metadata == metadata

class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics."""
    
    def test_from_empty_results(self):
        """Test performance metrics from empty results."""
        metrics = PerformanceMetrics.from_test_results([])
        
        assert metrics.total_execution_time_ms == 0
        assert metrics.average_execution_time_ms == 0
        assert metrics.peak_memory_usage_mb == 0
    
    def test_from_test_results(self):
        """Test performance metrics calculation."""
        results = [
            TestCaseResult("test_1", TestStatus.PASSED, execution_time_ms=100.0, memory_usage_mb=10.0),
            TestCaseResult("test_2", TestStatus.PASSED, execution_time_ms=200.0, memory_usage_mb=15.0),
            TestCaseResult("test_3", TestStatus.PASSED, execution_time_ms=150.0, memory_usage_mb=12.0)
        ]
        
        metrics = PerformanceMetrics.from_test_results(results)
        
        assert metrics.total_execution_time_ms == 450.0
        assert metrics.average_execution_time_ms == 150.0
        assert metrics.median_execution_time_ms == 150.0
        assert metrics.max_execution_time_ms == 200.0
        assert metrics.min_execution_time_ms == 100.0
        assert metrics.peak_memory_usage_mb == 15.0

class TestQualityMetrics:
    """Test cases for QualityMetrics."""
    
    def test_from_empty_results(self):
        """Test quality metrics from empty results."""
        metrics = QualityMetrics.from_test_results([])
        
        assert metrics.passed_tests == 0
        assert metrics.total_tests == 0
        assert metrics.pass_rate == 0.0
    
    def test_from_mixed_results(self):
        """Test quality metrics with mixed results."""
        results = [
            TestCaseResult("test_1", TestStatus.PASSED, similarity_score=1.0),
            TestCaseResult("test_2", TestStatus.FAILED, similarity_score=0.7),
            TestCaseResult("test_3", TestStatus.PASSED, similarity_score=1.0),
            TestCaseResult("test_4", TestStatus.ERROR, similarity_score=0.0)
        ]
        
        metrics = QualityMetrics.from_test_results(results)
        
        assert metrics.passed_tests == 2
        assert metrics.failed_tests == 1  # Only FAILED status, not ERROR
        assert metrics.total_tests == 4
        assert metrics.pass_rate == 0.5
        assert metrics.average_similarity_score == 0.675  # (1.0 + 0.7 + 1.0 + 0.0) / 4
        assert "FAILED" in metrics.error_types
        assert "ERROR" in metrics.error_types
    
    def test_correctness_score_calculation(self):
        """Test correctness score calculation."""
        # All passed with perfect similarity
        results = [
            TestCaseResult("test_1", TestStatus.PASSED, similarity_score=1.0),
            TestCaseResult("test_2", TestStatus.PASSED, similarity_score=1.0)
        ]
        
        metrics = QualityMetrics.from_test_results(results)
        
        # Correctness = (pass_rate * 0.8) + (avg_similarity * 0.2)
        # = (1.0 * 0.8) + (1.0 * 0.2) = 1.0
        assert metrics.correctness_score == 1.0

class TestTestResults:
    """Test cases for TestResults."""
    
    def test_overall_status_determination(self):
        """Test overall status determination logic."""
        # All passed
        results = [
            TestCaseResult("test_1", TestStatus.PASSED),
            TestCaseResult("test_2", TestStatus.PASSED)
        ]
        status = TestResults._determine_overall_status(results)
        assert status == OverallStatus.ALL_PASSED
        
        # All failed
        results = [
            TestCaseResult("test_1", TestStatus.FAILED),
            TestCaseResult("test_2", TestStatus.FAILED)
        ]
        status = TestResults._determine_overall_status(results)
        assert status == OverallStatus.ALL_FAILED
        
        # Mixed
        results = [
            TestCaseResult("test_1", TestStatus.PASSED),
            TestCaseResult("test_2", TestStatus.FAILED)
        ]
        status = TestResults._determine_overall_status(results)
        assert status == OverallStatus.PARTIAL_PASSED
        
        # Error cases
        results = [
            TestCaseResult("test_1", TestStatus.TIMEOUT)
        ]
        status = TestResults._determine_overall_status(results)
        assert status == OverallStatus.TIMEOUT_ERROR
    
    def test_from_execution_results(self):
        """Test creating TestResults from execution data."""
        test_cases = [
            TestCaseResult("test_1", TestStatus.PASSED, execution_time_ms=100.0),
            TestCaseResult("test_2", TestStatus.FAILED, execution_time_ms=150.0)
        ]
        
        results = TestResults.from_execution_results(
            execution_id="exec_123",
            problem_id="two-sum",
            language="python",
            test_case_results=test_cases,
            compilation_logs="Compilation successful",
            duration_ms=300.0
        )
        
        assert results.execution_id == "exec_123"
        assert results.problem_id == "two-sum"
        assert results.language == "python"
        assert results.overall_status == OverallStatus.PARTIAL_PASSED
        assert len(results.test_cases) == 2
        assert results.performance_metrics.total_execution_time_ms == 250.0
        assert results.quality_metrics.pass_rate == 0.5
    
    def test_get_summary(self):
        """Test summary generation."""
        test_cases = [
            TestCaseResult("test_1", TestStatus.PASSED, execution_time_ms=100.0),
            TestCaseResult("test_2", TestStatus.PASSED, execution_time_ms=150.0)
        ]
        
        results = TestResults.from_execution_results(
            execution_id="exec_123",
            problem_id="two-sum",
            language="python",
            test_case_results=test_cases
        )
        
        summary = results.get_summary()
        
        assert summary["execution_id"] == "exec_123"
        assert summary["problem_id"] == "two-sum"
        assert summary["language"] == "python"
        assert summary["overall_status"] == "ALL_PASSED"
        assert summary["passed_tests"] == 2
        assert summary["total_tests"] == 2
        assert summary["pass_rate"] == "100.0%"
    
    def test_detailed_report(self):
        """Test detailed report generation."""
        test_cases = [
            TestCaseResult("test_1", TestStatus.PASSED, execution_time_ms=100.0),
            TestCaseResult("test_2", TestStatus.FAILED, execution_time_ms=150.0)
        ]
        
        results = TestResults.from_execution_results(
            execution_id="exec_123",
            problem_id="two-sum",
            language="python",
            test_case_results=test_cases
        )
        
        report = results.get_detailed_report()
        
        assert "summary" in report
        assert "test_cases" in report
        assert "performance" in report
        assert "quality" in report
        assert "analysis" in report
        assert "recommendations" in report
        
        # Check analysis content
        analysis = report["analysis"]
        assert "strengths" in analysis
        assert "weaknesses" in analysis
        assert "patterns" in analysis
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        test_cases = [
            TestCaseResult("test_1", TestStatus.PASSED, execution_time_ms=100.0)
        ]
        
        original = TestResults.from_execution_results(
            execution_id="exec_123",
            problem_id="two-sum",
            language="python",
            test_case_results=test_cases
        )
        
        # Serialize to JSON
        json_str = original.to_json()
        assert isinstance(json_str, str)
        
        # Deserialize from JSON
        restored = TestResults.from_json(json_str)
        
        assert restored.execution_id == original.execution_id
        assert restored.problem_id == original.problem_id
        assert restored.language == original.language
        assert restored.overall_status == original.overall_status
        assert len(restored.test_cases) == len(original.test_cases)

class TestResultsAggregator:
    """Test cases for ResultsAggregator."""
    
    def test_empty_aggregator(self):
        """Test empty aggregator behavior."""
        aggregator = ResultsAggregator()
        
        stats = aggregator.get_overall_statistics()
        assert "error" in stats
        
        problem_stats = aggregator.get_problem_statistics("two-sum")
        assert "error" in problem_stats
    
    def test_add_and_aggregate_results(self):
        """Test adding results and aggregation."""
        aggregator = ResultsAggregator()
        
        # Add some test results
        for i in range(3):
            test_cases = [
                TestCaseResult(f"test_{j}", TestStatus.PASSED if j < i+1 else TestStatus.FAILED)
                for j in range(3)
            ]
            
            result = TestResults.from_execution_results(
                execution_id=f"exec_{i}",
                problem_id="two-sum",
                language="python",
                test_case_results=test_cases
            )
            
            aggregator.add_result(result)
        
        # Test overall statistics
        overall_stats = aggregator.get_overall_statistics()
        
        assert overall_stats["total_attempts"] == 3
        assert overall_stats["unique_problems"] == 1
        assert overall_stats["languages_used"] == 1
        assert overall_stats["most_common_language"] == "python"
    
    def test_problem_statistics(self):
        """Test problem-specific statistics."""
        aggregator = ResultsAggregator()
        
        # Add results for the same problem
        test_cases_1 = [TestCaseResult("test_1", TestStatus.PASSED)]
        test_cases_2 = [TestCaseResult("test_1", TestStatus.FAILED)]
        
        result1 = TestResults.from_execution_results(
            execution_id="exec_1",
            problem_id="two-sum",
            language="python",
            test_case_results=test_cases_1
        )
        
        result2 = TestResults.from_execution_results(
            execution_id="exec_2",
            problem_id="two-sum",
            language="java",
            test_case_results=test_cases_2
        )
        
        aggregator.add_result(result1)
        aggregator.add_result(result2)
        
        problem_stats = aggregator.get_problem_statistics("two-sum")
        
        assert problem_stats["problem_id"] == "two-sum"
        assert problem_stats["total_attempts"] == 2
        assert problem_stats["success_rate"] == 0.5  # 1 out of 2 passed
        assert set(problem_stats["languages_used"]) == {"python", "java"}
    
    def test_language_statistics(self):
        """Test language-specific statistics."""
        aggregator = ResultsAggregator()
        
        # Add results for the same language
        test_cases = [TestCaseResult("test_1", TestStatus.PASSED)]
        
        result1 = TestResults.from_execution_results(
            execution_id="exec_1",
            problem_id="two-sum",
            language="python",
            test_case_results=test_cases
        )
        
        result2 = TestResults.from_execution_results(
            execution_id="exec_2",
            problem_id="valid-parentheses",
            language="python",
            test_case_results=test_cases
        )
        
        aggregator.add_result(result1)
        aggregator.add_result(result2)
        
        lang_stats = aggregator.get_language_statistics("python")
        
        assert lang_stats["language"] == "python"
        assert lang_stats["total_attempts"] == 2
        assert lang_stats["problems_solved"] == 2
        assert lang_stats["average_success_rate"] == 1.0

class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    def test_complete_workflow(self):
        """Test complete workflow from test cases to aggregated results."""
        # Create test case results
        test_cases = [
            TestCaseResult(
                test_id="test_1",
                status=TestStatus.PASSED,
                input_data="[2,7,11,15], 9",
                expected_output="[0,1]",
                actual_output="[0,1]",
                execution_time_ms=45.0,
                memory_usage_mb=8.0,
                similarity_score=1.0,
                comparator_used="ArrayComparator"
            ),
            TestCaseResult(
                test_id="test_2",
                status=TestStatus.FAILED,
                input_data="[3,2,4], 6",
                expected_output="[1,2]",
                actual_output="[0,2]",
                execution_time_ms=52.0,
                memory_usage_mb=9.0,
                similarity_score=0.5,
                comparator_used="ArrayComparator",
                diff_details="Index 0: expected 1, got 0"
            )
        ]
        
        # Create test results
        results = TestResults.from_execution_results(
            execution_id="exec_integration_test",
            problem_id="two-sum",
            language="python",
            test_case_results=test_cases,
            compilation_logs="Compilation successful",
            runtime_logs="",
            duration_ms=120.0
        )
        
        # Verify results structure
        assert results.overall_status == OverallStatus.PARTIAL_PASSED
        assert results.quality_metrics.pass_rate == 0.5
        assert results.performance_metrics.average_execution_time_ms == 48.5
        
        # Test detailed report
        report = results.get_detailed_report()
        assert len(report["test_cases"]) == 2
        assert "recommendations" in report
        
        # Test aggregation
        aggregator = ResultsAggregator()
        aggregator.add_result(results)
        
        overall_stats = aggregator.get_overall_statistics()
        assert overall_stats["total_attempts"] == 1
        assert overall_stats["unique_problems"] == 1
    
    def test_performance_analysis(self):
        """Test performance analysis features."""
        # Create results with varying performance
        test_cases = [
            TestCaseResult("test_1", TestStatus.PASSED, execution_time_ms=10.0),
            TestCaseResult("test_2", TestStatus.PASSED, execution_time_ms=100.0),
            TestCaseResult("test_3", TestStatus.PASSED, execution_time_ms=1000.0)
        ]
        
        results = TestResults.from_execution_results(
            execution_id="perf_test",
            problem_id="performance-test",
            language="python",
            test_case_results=test_cases
        )
        
        # Check performance metrics
        perf = results.performance_metrics
        assert perf.min_execution_time_ms == 10.0
        assert perf.max_execution_time_ms == 1000.0
        assert perf.median_execution_time_ms == 100.0
        
        # Check analysis
        report = results.get_detailed_report()
        analysis = report["analysis"]
        
        # Should detect slow execution
        assert any("slow" in weakness.lower() for weakness in analysis["weaknesses"])

if __name__ == "__main__":
    pytest.main([__file__])