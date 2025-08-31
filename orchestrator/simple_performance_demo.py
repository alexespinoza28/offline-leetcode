#!/usr/bin/env python3
"""
Simple performance monitoring demo without external dependencies.
This script demonstrates basic performance monitoring capabilities
without requiring psutil or other external libraries.
"""
import time
import threading
from typing import Dict, Any, List
from datetime import datetime
import json

class SimpleProfiler:
    """Basic profiler without external dependencies."""
    
    def __init__(self):
        self.function_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def profile_function(self, func_name: str = None):
        """Simple profiling decorator."""
        def decorator(func):
            nonlocal func_name
            if func_name is None:
                func_name = f"{func.__module__}.{func.__name__}"
            
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.perf_counter() - start_time
                    self._record_execution(func_name, execution_time, success=True)
                    return result
                except Exception as e:
                    execution_time = time.perf_counter() - start_time
                    self._record_execution(func_name, execution_time, success=False, error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    def _record_execution(self, func_name: str, execution_time: float, success: bool = True, error: str = None):
        """Record function execution statistics."""
        with self._lock:
            if func_name not in self.function_stats:
                self.function_stats[func_name] = {
                    "call_count": 0,
                    "total_time": 0.0,
                    "min_time": float('inf'),
                    "max_time": 0.0,
                    "avg_time": 0.0,
                    "success_count": 0,
                    "error_count": 0,
                    "last_error": None
                }
            
            stats = self.function_stats[func_name]
            stats["call_count"] += 1
            stats["total_time"] += execution_time
            stats["min_time"] = min(stats["min_time"], execution_time)
            stats["max_time"] = max(stats["max_time"], execution_time)
            stats["avg_time"] = stats["total_time"] / stats["call_count"]
            
            if success:
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
                stats["last_error"] = error
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all profiling statistics."""
        with self._lock:
            return dict(self.function_stats)
    
    def get_slowest_functions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the slowest functions."""
        with self._lock:
            sorted_functions = sorted(
                self.function_stats.items(),
                key=lambda x: x[1]["avg_time"],
                reverse=True
            )
            return [
                {"function": name, **stats}
                for name, stats in sorted_functions[:limit]
            ]

class SimpleCache:
    """Basic cache implementation without external dependencies."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order: List[str] = []
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str, default=None):
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                self.hits += 1
                return self._cache[key]["value"]
            else:
                self.misses += 1
                return default
    
    def set(self, key: str, value):
        """Set value in cache."""
        with self._lock:
            if key in self._cache:
                # Update existing
                self._cache[key]["value"] = value
                self._cache[key]["timestamp"] = datetime.now()
                # Move to end
                self._access_order.remove(key)
                self._access_order.append(key)
            else:
                # Add new
                if len(self._cache) >= self.max_size:
                    # Remove least recently used
                    lru_key = self._access_order.pop(0)
                    del self._cache[lru_key]
                
                self._cache[key] = {
                    "value": value,
                    "timestamp": datetime.now()
                }
                self._access_order.append(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

# Global instances
profiler = SimpleProfiler()
cache = SimpleCache()

def cached(func):
    """Simple caching decorator."""
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute function and cache result
        result = func(*args, **kwargs)
        cache.set(cache_key, result)
        return result
    
    return wrapper

# Demo functions
@profiler.profile_function()
def slow_function():
    """Simulate a slow function."""
    time.sleep(0.1)
    return "slow_result"

@profiler.profile_function()
def fast_function():
    """Simulate a fast function."""
    time.sleep(0.01)
    return "fast_result"

@cached
@profiler.profile_function()
def expensive_computation(n: int):
    """Simulate expensive computation that benefits from caching."""
    time.sleep(0.05)  # Simulate computation time
    return sum(i * i for i in range(n))

@profiler.profile_function()
def failing_function():
    """Function that sometimes fails."""
    import random
    if random.random() < 0.3:  # 30% chance of failure
        raise ValueError("Random failure for demo")
    time.sleep(0.02)
    return "success"

def demo_profiling():
    """Demonstrate profiling capabilities."""
    print("=== Performance Profiling Demo ===")
    
    # Call functions multiple times
    for i in range(10):
        slow_function()
        fast_function()
        expensive_computation(100)
        
        # Try failing function
        try:
            failing_function()
        except ValueError:
            pass  # Expected failures
    
    # Show statistics
    stats = profiler.get_stats()
    print(f"Profiled {len(stats)} functions:")
    
    for func_name, func_stats in stats.items():
        print(f"\n{func_name}:")
        print(f"  Calls: {func_stats['call_count']}")
        print(f"  Avg time: {func_stats['avg_time']:.4f}s")
        print(f"  Min time: {func_stats['min_time']:.4f}s")
        print(f"  Max time: {func_stats['max_time']:.4f}s")
        print(f"  Success rate: {func_stats['success_count']}/{func_stats['call_count']}")
        if func_stats['error_count'] > 0:
            print(f"  Last error: {func_stats['last_error']}")
    
    # Show slowest functions
    print("\nSlowest functions:")
    slowest = profiler.get_slowest_functions(3)
    for i, func_info in enumerate(slowest, 1):
        print(f"  {i}. {func_info['function']}: {func_info['avg_time']:.4f}s avg")

def demo_caching():
    """Demonstrate caching functionality."""
    print("\n=== Caching Demo ===")
    
    # First calls - will be slow and cached
    print("First calls (will be cached):")
    start_time = time.time()
    result1 = expensive_computation(1000)
    first_time = time.time() - start_time
    print(f"  expensive_computation(1000): {first_time:.4f}s")
    
    start_time = time.time()
    result2 = expensive_computation(500)
    second_time = time.time() - start_time
    print(f"  expensive_computation(500): {second_time:.4f}s")
    
    # Second calls - should be fast (from cache)
    print("\nSecond calls (from cache):")
    start_time = time.time()
    result3 = expensive_computation(1000)
    cached_time1 = time.time() - start_time
    print(f"  expensive_computation(1000): {cached_time1:.4f}s (speedup: {first_time/cached_time1:.1f}x)")
    
    start_time = time.time()
    result4 = expensive_computation(500)
    cached_time2 = time.time() - start_time
    print(f"  expensive_computation(500): {cached_time2:.4f}s (speedup: {second_time/cached_time2:.1f}x)")
    
    # Show cache statistics
    cache_stats = cache.get_stats()
    print(f"\nCache statistics:")
    print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"  Hits: {cache_stats['hits']}")
    print(f"  Misses: {cache_stats['misses']}")
    print(f"  Hit rate: {cache_stats['hit_rate']:.1f}%")

def demo_performance_analysis():
    """Demonstrate performance analysis."""
    print("\n=== Performance Analysis ===")
    
    # Analyze current performance
    stats = profiler.get_stats()
    cache_stats = cache.get_stats()
    
    # Calculate overall metrics
    total_calls = sum(s["call_count"] for s in stats.values())
    total_time = sum(s["total_time"] for s in stats.values())
    total_errors = sum(s["error_count"] for s in stats.values())
    
    print(f"Overall Performance:")
    print(f"  Total function calls: {total_calls}")
    print(f"  Total execution time: {total_time:.4f}s")
    print(f"  Average time per call: {total_time/total_calls:.4f}s")
    print(f"  Error rate: {total_errors/total_calls*100:.1f}%")
    print(f"  Cache hit rate: {cache_stats['hit_rate']:.1f}%")
    
    # Identify performance issues
    issues = []
    
    # Check for slow functions
    for func_name, func_stats in stats.items():
        if func_stats["avg_time"] > 0.05:  # 50ms threshold
            issues.append(f"Slow function: {func_name} ({func_stats['avg_time']:.4f}s avg)")
    
    # Check cache performance
    if cache_stats["hit_rate"] < 70:
        issues.append(f"Low cache hit rate: {cache_stats['hit_rate']:.1f}%")
    
    # Check error rates
    for func_name, func_stats in stats.items():
        error_rate = func_stats["error_count"] / func_stats["call_count"] * 100
        if error_rate > 10:  # 10% threshold
            issues.append(f"High error rate: {func_name} ({error_rate:.1f}%)")
    
    if issues:
        print(f"\nPerformance Issues Identified ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
        
        print(f"\nRecommendations:")
        print(f"  - Profile slow functions to identify bottlenecks")
        print(f"  - Increase cache size or TTL to improve hit rates")
        print(f"  - Add error handling and retry logic for failing functions")
        print(f"  - Consider async execution for I/O bound operations")
    else:
        print(f"\nNo significant performance issues detected! ✅")

def main():
    """Run the complete performance monitoring demo."""
    print("Interview Coding Platform - Simple Performance Demo")
    print("=" * 60)
    
    try:
        demo_profiling()
        demo_caching()
        demo_performance_analysis()
        
        print("\n=== Demo Complete ===")
        print("Basic performance monitoring is working correctly!")
        
        # Export results
        report = {
            "timestamp": datetime.now().isoformat(),
            "profiling_stats": profiler.get_stats(),
            "cache_stats": cache.get_stats(),
            "slowest_functions": profiler.get_slowest_functions(5)
        }
        
        with open('simple_performance_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print("Performance report exported to simple_performance_report.json")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()