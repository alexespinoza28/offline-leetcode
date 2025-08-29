"""
Performance monitoring integration for the execution system.
This module integrates performance monitoring into the existing
code execution and testing infrastructure.
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .profiler import profiler, profile

logger = logging.getLogger(__name__)

class ExecutionMonitor:
    """
    Monitor performance of code execution operations.
    Integrates with the existing execution system to track:
    - Code compilation times
    - Test execution performance
    - Resource usage patterns
    - Error rates by language
    """
    
    def __init__(self):
        self.execution_stats: Dict[str, Dict[str, Any]] = {}
        self.language_stats: Dict[str, Dict[str, Any]] = {}
    
    @profile(include_memory=True, include_cpu=True)
    def monitor_compilation(self, language: str, code_size: int, func):
        """Monitor code compilation performance."""
        start_time = time.perf_counter()
        
        try:
            result = func()
            execution_time = time.perf_counter() - start_time
            
            # Update language-specific stats
            if language not in self.language_stats:
                self.language_stats[language] = {
                    "compilation_count": 0,
                    "total_compilation_time": 0.0,
                    "avg_compilation_time": 0.0,
                    "compilation_errors": 0,
                    "total_code_size": 0,
                    "avg_code_size": 0.0
                }
            
            stats = self.language_stats[language]
            stats["compilation_count"] += 1
            stats["total_compilation_time"] += execution_time
            stats["avg_compilation_time"] = stats["total_compilation_time"] / stats["compilation_count"]
            stats["total_code_size"] += code_size
            stats["avg_code_size"] = stats["total_code_size"] / stats["compilation_count"]
            
            if not result.success:
                stats["compilation_errors"] += 1
            
            logger.debug(f"Compilation {language}: {execution_time:.3f}s, size: {code_size} bytes")
            return result
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            if language in self.language_stats:
                self.language_stats[language]["compilation_errors"] += 1
            logger.error(f"Compilation monitoring error for {language}: {e}")
            raise
    
    @profile(include_memory=True, include_cpu=True)
    def monitor_execution(self, language: str, test_count: int, func):
        """Monitor test execution performance."""
        start_time = time.perf_counter()
        
        try:
            result = func()
            execution_time = time.perf_counter() - start_time
            
            # Update execution stats
            execution_key = f"{language}_execution"
            if execution_key not in self.execution_stats:
                self.execution_stats[execution_key] = {
                    "execution_count": 0,
                    "total_execution_time": 0.0,
                    "avg_execution_time": 0.0,
                    "total_tests_run": 0,
                    "avg_tests_per_execution": 0.0,
                    "successful_executions": 0,
                    "failed_executions": 0
                }
            
            stats = self.execution_stats[execution_key]
            stats["execution_count"] += 1
            stats["total_execution_time"] += execution_time
            stats["avg_execution_time"] = stats["total_execution_time"] / stats["execution_count"]
            stats["total_tests_run"] += test_count
            stats["avg_tests_per_execution"] = stats["total_tests_run"] / stats["execution_count"]
            
            if hasattr(result, 'passed') and result.passed == result.total:
                stats["successful_executions"] += 1
            else:
                stats["failed_executions"] += 1
            
            logger.debug(f"Execution {language}: {execution_time:.3f}s, {test_count} tests")
            return result
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            execution_key = f"{language}_execution"
            if execution_key in self.execution_stats:
                self.execution_stats[execution_key]["failed_executions"] += 1
            logger.error(f"Execution monitoring error for {language}: {e}")
            raise
    
    def get_language_performance(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics by language."""
        if language:
            return self.language_stats.get(language, {})
        return dict(self.language_stats)
    
    def get_execution_performance(self) -> Dict[str, Any]:
        """Get execution performance statistics."""
        return dict(self.execution_stats)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "language_stats": self.language_stats,
            "execution_stats": self.execution_stats,
            "system_performance": profiler.generate_performance_report()
        }
        
        # Calculate overall metrics
        total_compilations = sum(
            stats.get("compilation_count", 0) 
            for stats in self.language_stats.values()
        )
        total_executions = sum(
            stats.get("execution_count", 0) 
            for stats in self.execution_stats.values()
        )
        
        summary["overall_metrics"] = {
            "total_compilations": total_compilations,
            "total_executions": total_executions,
            "most_used_language": self._get_most_used_language(),
            "average_compilation_time": self._get_average_compilation_time(),
            "average_execution_time": self._get_average_execution_time()
        }
        
        return summary
    
    def _get_most_used_language(self) -> Optional[str]:
        """Get the most frequently used language."""
        if not self.language_stats:
            return None
        
        return max(
            self.language_stats.items(),
            key=lambda x: x[1].get("compilation_count", 0)
        )[0]
    
    def _get_average_compilation_time(self) -> float:
        """Get overall average compilation time."""
        total_time = sum(
            stats.get("total_compilation_time", 0) 
            for stats in self.language_stats.values()
        )
        total_count = sum(
            stats.get("compilation_count", 0) 
            for stats in self.language_stats.values()
        )
        
        return total_time / total_count if total_count > 0 else 0.0
    
    def _get_average_execution_time(self) -> float:
        """Get overall average execution time."""
        total_time = sum(
            stats.get("total_execution_time", 0) 
            for stats in self.execution_stats.values()
        )
        total_count = sum(
            stats.get("execution_count", 0) 
            for stats in self.execution_stats.values()
        )
        
        return total_time / total_count if total_count > 0 else 0.0
    
    def reset_stats(self):
        """Reset all monitoring statistics."""
        self.execution_stats.clear()
        self.language_stats.clear()
        logger.info("Performance monitoring statistics reset")

# Global monitor instance
execution_monitor = ExecutionMonitor()

def monitor_compilation(language: str, code_size: int):
    """Decorator to monitor compilation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return execution_monitor.monitor_compilation(language, code_size, lambda: func(*args, **kwargs))
        return wrapper
    return decorator

def monitor_execution(language: str, test_count: int):
    """Decorator to monitor execution performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return execution_monitor.monitor_execution(language, test_count, lambda: func(*args, **kwargs))
        return wrapper
    return decorator

def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return execution_monitor.get_performance_summary()