"""
Performance optimization service for the Interview Coding Platform.
This module provides automated performance optimization strategies
and recommendations based on collected metrics.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from .profiler import profiler
from .monitor import execution_monitor
from .cache import get_cache_stats, clear_all_caches

logger = logging.getLogger(__name__)

@dataclass
class OptimizationRecommendation:
    """Represents a performance optimization recommendation."""
    category: str
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    impact: str
    implementation: str

class PerformanceOptimizer:
    """
    Automated performance optimization and recommendation system.
    Analyzes performance metrics and provides actionable recommendations
    for improving system performance.
    """
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Comprehensive performance analysis.
        Returns analysis results with metrics, issues, and recommendations.
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self._collect_current_metrics(),
            "issues": self._identify_performance_issues(),
            "recommendations": self._generate_recommendations()
        }
        
        return analysis
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics from various sources."""
        metrics = {}
        
        # Function performance metrics
        function_stats = profiler.get_function_stats()
        if function_stats:
            avg_times = [stats.get("avg_time", 0) for stats in function_stats.values()]
            metrics["avg_function_time"] = sum(avg_times) / len(avg_times) if avg_times else 0
            metrics["max_function_time"] = max(avg_times) if avg_times else 0
            metrics["total_function_calls"] = sum(
                stats.get("call_count", 0) for stats in function_stats.values()
            )
        
        # Execution monitoring metrics
        execution_perf = execution_monitor.get_performance_summary()
        metrics["execution_performance"] = execution_perf
        
        # Cache performance
        cache_stats = get_cache_stats()
        metrics["cache_stats"] = cache_stats
        
        return metrics
    
    def _identify_performance_issues(self) -> List[Dict[str, Any]]:
        """Identify current performance issues based on thresholds."""
        issues = []
        metrics = self._collect_current_metrics()
        
        # Check for slow functions
        avg_function_time = metrics.get("avg_function_time", 0)
        if avg_function_time > 1.0:  # 1 second threshold
            issues.append({
                "severity": "warning",
                "category": "response_time",
                "message": f"Average function execution time is {avg_function_time:.2f}s",
                "current_value": avg_function_time
            })
        
        # Check cache performance
        cache_stats = metrics.get("cache_stats", {})
        for cache_name, stats in cache_stats.items():
            hit_rate = stats.get("hit_rate", 100)
            if hit_rate < 70:  # 70% hit rate threshold
                issues.append({
                    "severity": "warning",
                    "category": "cache_performance",
                    "message": f"{cache_name} hit rate is only {hit_rate:.1f}%",
                    "current_value": hit_rate
                })
        
        # Check for compilation errors
        execution_perf = metrics.get("execution_performance", {})
        language_stats = execution_perf.get("language_stats", {})
        for language, stats in language_stats.items():
            error_rate = 0
            if stats.get("compilation_count", 0) > 0:
                error_rate = stats.get("compilation_errors", 0) / stats["compilation_count"] * 100
            
            if error_rate > 10:  # 10% error rate threshold
                issues.append({
                    "severity": "warning",
                    "category": "compilation_errors",
                    "message": f"{language} compilation error rate is {error_rate:.1f}%",
                    "current_value": error_rate
                })
        
        return issues
    
    def _generate_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        issues = self._identify_performance_issues()
        metrics = self._collect_current_metrics()
        
        # Analyze slow functions
        slowest_functions = profiler.get_slowest_functions(3)
        if slowest_functions and slowest_functions[0].get("avg_time", 0) > 0.5:
            recommendations.append(OptimizationRecommendation(
                category="function_optimization",
                priority="high",
                title="Optimize Slow Functions",
                description=f"Function '{slowest_functions[0]['function']}' has average execution time of {slowest_functions[0]['avg_time']:.2f}s",
                impact="Reducing execution time by 50% could improve overall response time significantly",
                implementation="Profile the function, optimize algorithms, add caching, or consider async execution"
            ))
        
        # Cache optimization recommendations
        cache_stats = metrics.get("cache_stats", {})
        for cache_name, stats in cache_stats.items():
            hit_rate = stats.get("hit_rate", 100)
            if hit_rate < 80:
                recommendations.append(OptimizationRecommendation(
                    category="cache_optimization",
                    priority="medium",
                    title=f"Improve {cache_name} Hit Rate",
                    description=f"Current hit rate is {hit_rate:.1f}%, which is below optimal",
                    impact="Improving cache hit rate to 90%+ can significantly reduce computation time",
                    implementation="Review cache TTL settings, increase cache size, or implement better caching strategies"
                ))
        
        # Language-specific recommendations
        execution_perf = metrics.get("execution_performance", {})
        language_stats = execution_perf.get("language_stats", {})
        
        for language, stats in language_stats.items():
            avg_compilation_time = stats.get("avg_compilation_time", 0)
            if avg_compilation_time > 2.0:  # 2 second compilation threshold
                recommendations.append(OptimizationRecommendation(
                    category="compilation_optimization",
                    priority="medium",
                    title=f"Optimize {language} Compilation",
                    description=f"Average compilation time is {avg_compilation_time:.2f}s",
                    impact="Faster compilation improves development experience",
                    implementation="Consider compilation caching, incremental compilation, or compiler optimization flags"
                ))
        
        return recommendations
    
    def apply_automatic_optimizations(self) -> Dict[str, Any]:
        """
        Apply safe automatic optimizations.
        Returns results of applied optimizations.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [],
            "errors": []
        }
        
        try:
            # Clear expired cache entries
            clear_all_caches()
            results["optimizations_applied"].append({
                "type": "cache_cleanup",
                "description": "Cleared all cache entries to free memory",
                "impact": "Freed memory and reset cache statistics"
            })
            
        except Exception as e:
            results["errors"].append({
                "type": "automatic_optimization_error",
                "error": str(e)
            })
            logger.error(f"Error in automatic optimization: {e}")
        
        # Record optimization in history
        self.optimization_history.append(results)
        
        return results
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get history of applied optimizations."""
        return list(self.optimization_history)

# Global optimizer instance
optimizer = PerformanceOptimizer()

def analyze_performance() -> Dict[str, Any]:
    """Get comprehensive performance analysis."""
    return optimizer.analyze_performance()

def apply_optimizations() -> Dict[str, Any]:
    """Apply automatic performance optimizations."""
    return optimizer.apply_automatic_optimizations()

def get_recommendations() -> List[OptimizationRecommendation]:
    """Get current optimization recommendations."""
    analysis = optimizer.analyze_performance()
    return analysis.get("recommendations", [])