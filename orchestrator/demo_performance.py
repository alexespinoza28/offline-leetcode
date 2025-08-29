#!/usr/bin/env python3
"""
Demo script for the performance monitoring and optimization system.
This script demonstrates how to use the performance monitoring tools
to profile and optimize the Interview Coding Platform.
"""
import time
import json
from performance.profiler import profile, get_performance_report
from performance.monitor import monitor_compilation, monitor_execution, get_performance_summary
from performance.cache import cached, get_cache_stats, clear_all_caches
from performance.optimizer import analyze_performance, apply_optimizations, get_recommendations

# Example functions to demonstrate profiling
@profile(include_memory=True, include_cpu=True)
def slow_function():
    """Simulate a slow function for demonstration."""
    time.sleep(0.1)  # Simulate work
    return "completed"

@cached(ttl=300)  # Cache for 5 minutes
def expensive_computation(n: int):
    """Simulate an expensive computation that benefits from caching."""
    time.sleep(0.05)  # Simulate computation time
    return sum(i * i for i in range(n))

@monitor_compilation("python", 1000)
def simulate_compilation():
    """Simulate code compilation for monitoring."""
    time.sleep(0.02)  # Simulate compilation time
    return type('CompileResult', (), {'success': True, 'output': '', 'errors': ''})()

@monitor_execution("python", 5)
def simulate_execution():
    """Simulate test execution for monitoring."""
    time.sleep(0.03)  # Simulate execution time
    return type('TestResult', (), {'passed': 5, 'total': 5, 'results': []})()

def demo_profiling():
    """Demonstrate function profiling capabilities."""
    print("=== Performance Profiling Demo ===")
    
    # Call functions multiple times to generate statistics
    for i in range(10):
        slow_function()
        expensive_computation(100)
        simulate_compilation()
        simulate_execution()
    
    # Get performance report
    report = get_performance_report()
    print(f"Total functions profiled: {report['summary']['total_functions_profiled']}")
    print(f"Total function calls: {report['summary']['total_function_calls']}")
    print(f"Total execution time: {report['summary']['total_execution_time']:.3f}s")
    
    # Show slowest functions
    print("\nSlowest functions:")
    for func in report['slowest_functions']:
        print(f"  {func['function']}: {func['avg_time']:.3f}s avg ({func['call_count']} calls)")

def demo_caching():
    """Demonstrate caching functionality."""
    print("\n=== Caching Demo ===")
    
    # First call - will be slow and cached
    start_time = time.time()
    result1 = expensive_computation(1000)
    first_call_time = time.time() - start_time
    
    # Second call - should be fast (from cache)
    start_time = time.time()
    result2 = expensive_computation(1000)
    second_call_time = time.time() - start_time
    
    print(f"First call time: {first_call_time:.3f}s")
    print(f"Second call time: {second_call_time:.3f}s")
    print(f"Speedup: {first_call_time / second_call_time:.1f}x")
    
    # Show cache statistics
    cache_stats = get_cache_stats()
    print("\nCache statistics:")
    for cache_name, stats in cache_stats.items():
        print(f"  {cache_name}: {stats['hits']} hits, {stats['misses']} misses, {stats['hit_rate']:.1f}% hit rate")

def demo_monitoring():
    """Demonstrate execution monitoring."""
    print("\n=== Execution Monitoring Demo ===")
    
    # Simulate multiple compilations and executions
    for i in range(5):
        simulate_compilation()
        simulate_execution()
    
    # Get monitoring summary
    summary = get_performance_summary()
    
    print("Language performance:")
    for language, stats in summary.get('language_stats', {}).items():
        print(f"  {language}:")
        print(f"    Compilations: {stats['compilation_count']}")
        print(f"    Avg compilation time: {stats['avg_compilation_time']:.3f}s")
        print(f"    Compilation errors: {stats['compilation_errors']}")
    
    print("\nExecution performance:")
    for exec_type, stats in summary.get('execution_stats', {}).items():
        print(f"  {exec_type}:")
        print(f"    Executions: {stats['execution_count']}")
        print(f"    Avg execution time: {stats['avg_execution_time']:.3f}s")
        print(f"    Success rate: {stats['successful_executions']}/{stats['execution_count']}")

def demo_optimization():
    """Demonstrate performance analysis and optimization."""
    print("\n=== Performance Optimization Demo ===")
    
    # Analyze current performance
    analysis = analyze_performance()
    
    print("Performance Analysis:")
    print(f"  Timestamp: {analysis['timestamp']}")
    
    # Show identified issues
    issues = analysis.get('issues', [])
    if issues:
        print(f"\nIdentified {len(issues)} performance issues:")
        for issue in issues:
            print(f"  [{issue['severity'].upper()}] {issue['message']}")
    else:
        print("\nNo performance issues identified.")
    
    # Show recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        print(f"\nOptimization recommendations ({len(recommendations)}):")
        for rec in recommendations:
            print(f"  [{rec.priority.upper()}] {rec.title}")
            print(f"    {rec.description}")
            print(f"    Impact: {rec.impact}")
            print(f"    Implementation: {rec.implementation}")
            print()
    else:
        print("\nNo optimization recommendations at this time.")
    
    # Apply automatic optimizations
    print("Applying automatic optimizations...")
    optimization_results = apply_optimizations()
    
    applied = optimization_results.get('optimizations_applied', [])
    if applied:
        print(f"Applied {len(applied)} optimizations:")
        for opt in applied:
            print(f"  - {opt['description']}")
    
    errors = optimization_results.get('errors', [])
    if errors:
        print(f"Encountered {len(errors)} errors during optimization:")
        for error in errors:
            print(f"  - {error['error']}")

def main():
    """Run the complete performance monitoring demo."""
    print("Interview Coding Platform - Performance Monitoring Demo")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_profiling()
        demo_caching()
        demo_monitoring()
        demo_optimization()
        
        print("\n=== Demo Complete ===")
        print("Performance monitoring system is working correctly!")
        
        # Export final analysis
        final_analysis = analyze_performance()
        with open('performance_analysis.json', 'w') as f:
            json.dump(final_analysis, f, indent=2, default=str)
        print("Final analysis exported to performance_analysis.json")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()