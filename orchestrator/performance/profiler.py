"""
Performance profiling utilities for the Interview Coding Platform.
This module provides comprehensive performance monitoring and profiling
capabilities to identify bottlenecks and optimize system performance.
"""
import time
import psutil
import threading
import functools
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Represents a single performance measurement."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProfileResult:
    """Results from a performance profiling session."""
    function_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    call_count: int
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

class PerformanceProfiler:
    """
    Comprehensive performance profiler for monitoring system performance.
    Features:
    - Function execution timing
    - Memory usage tracking
    - CPU usage monitoring
    - Call frequency analysis
    - Performance trend analysis
    """
    
    def __init__(self, enable_detailed_profiling: bool = True):
        self.enable_detailed_profiling = enable_detailed_profiling
        self.metrics: List[PerformanceMetric] = []
        self.profile_results: List[ProfileResult] = []
        self.function_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
        # System monitoring
        self.process = psutil.Process()
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
    
    def profile_function(self, include_memory: bool = True, include_cpu: bool = True):
        """
        Decorator to profile function performance.
        
        Args:
            include_memory: Whether to track memory usage
            include_cpu: Whether to track CPU usage
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._profile_execution(
                    func, args, kwargs, include_memory, include_cpu
                )
            return wrapper
        return decorator
    
    def _profile_execution(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: dict,
        include_memory: bool,
        include_cpu: bool
    ) -> Any:
        """Execute function with performance profiling."""
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Pre-execution measurements
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss if include_memory else 0
        start_cpu = self.process.cpu_percent() if include_cpu else 0
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Post-execution measurements
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            end_memory = self.process.memory_info().rss if include_memory else 0
            memory_delta = end_memory - start_memory if include_memory else 0
            
            end_cpu = self.process.cpu_percent() if include_cpu else 0
            cpu_usage = (start_cpu + end_cpu) / 2 if include_cpu else 0
            
            # Record results
            self._record_profile_result(
                func_name, execution_time, memory_delta, cpu_usage
            )
            
            return result
            
        except Exception as e:
            # Record failed execution
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            self._record_profile_result(
                func_name, execution_time, 0, 0, 
                context={"error": str(e), "exception_type": type(e).__name__}
            )
            raise
    
    def _record_profile_result(
        self, 
        func_name: str, 
        execution_time: float,
        memory_usage: float, 
        cpu_usage: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record profiling results."""
        with self._lock:
            # Update function statistics
            if func_name not in self.function_stats:
                self.function_stats[func_name] = {
                    "call_count": 0,
                    "total_time": 0.0,
                    "min_time": float('inf'),
                    "max_time": 0.0,
                    "avg_time": 0.0,
                    "total_memory": 0.0,
                    "avg_memory": 0.0,
                    "total_cpu": 0.0,
                    "avg_cpu": 0.0,
                    "errors": 0
                }
            
            stats = self.function_stats[func_name]
            stats["call_count"] += 1
            stats["total_time"] += execution_time
            stats["min_time"] = min(stats["min_time"], execution_time)
            stats["max_time"] = max(stats["max_time"], execution_time)
            stats["avg_time"] = stats["total_time"] / stats["call_count"]
            
            if memory_usage != 0:
                stats["total_memory"] += memory_usage
                stats["avg_memory"] = stats["total_memory"] / stats["call_count"]
            
            if cpu_usage != 0:
                stats["total_cpu"] += cpu_usage
                stats["avg_cpu"] = stats["total_cpu"] / stats["call_count"]
            
            if context and "error" in context:
                stats["errors"] += 1
            
            # Store detailed result
            if self.enable_detailed_profiling:
                result = ProfileResult(
                    function_name=func_name,
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    cpu_usage=cpu_usage,
                    call_count=stats["call_count"],
                    timestamp=datetime.now(),
                    context=context or {}
                )
                self.profile_results.append(result)
    
    def get_function_stats(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """Get function performance statistics."""
        with self._lock:
            if func_name:
                return self.function_stats.get(func_name, {})
            return dict(self.function_stats)
    
    def get_slowest_functions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest functions by average execution time."""
        with self._lock:
            sorted_functions = sorted(
                self.function_stats.items(),
                key=lambda x: x[1].get("avg_time", 0),
                reverse=True
            )
            return [
                {"function": name, **stats}
                for name, stats in sorted_functions[:limit]
            ]
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        with self._lock:
            report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_functions_profiled": len(self.function_stats),
                    "total_function_calls": sum(
                        stats.get("call_count", 0) 
                        for stats in self.function_stats.values()
                    ),
                    "total_execution_time": sum(
                        stats.get("total_time", 0) 
                        for stats in self.function_stats.values()
                    ),
                    "total_errors": sum(
                        stats.get("errors", 0) 
                        for stats in self.function_stats.values()
                    )
                },
                "slowest_functions": self.get_slowest_functions(5),
                "system_metrics": {
                    "current_cpu": psutil.cpu_percent(),
                    "current_memory": psutil.virtual_memory().percent,
                    "process_memory_mb": self.process.memory_info().rss / 1024 / 1024,
                    "process_cpu": self.process.cpu_percent()
                }
            }
            return report

# Global profiler instance
profiler = PerformanceProfiler()

def profile(include_memory: bool = True, include_cpu: bool = True):
    """Convenience decorator for profiling functions."""
    return profiler.profile_function(include_memory, include_cpu)

def get_performance_report() -> Dict[str, Any]:
    """Get current performance report."""
    return profiler.generate_performance_report()