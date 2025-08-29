#!/usr/bin/env python3
"""
Tests for the performance monitoring and optimization system.
"""
import unittest
import time
import threading
from unittest.mock import patch, MagicMock
from performance.profiler import PerformanceProfiler, profile
from performance.monitor import ExecutionMonitor, monitor_compilation, monitor_execution
from performance.cache import SimpleCache, cached, get_cache_stats
from performance.optimizer import PerformanceOptimizer

class TestPerformanceProfiler(unittest.TestCase):
    """Test the performance profiler functionality."""
    
    def setUp(self):
        self.profiler = PerformanceProfiler()
    
    def test_profile_decorator(self):
        """Test the profile decorator functionality."""
        @self.profiler.profile_function()
        def test_function(x, y):
            time.sleep(0.01)  # Small delay for testing
            return x + y
        
        result = test_function(1, 2)
        self.assertEqual(result, 3)
        
        # Check that profiling data was recorded
        stats = self.profiler.get_function_stats()
        self.assertGreater(len(stats), 0)
        
        func_name = f"{test_function.__module__}.{test_function.__name__}"
        self.assertIn(func_name, stats)
        self.assertEqual(stats[func_name]["call_count"], 1)
        self.assertGreater(stats[func_name]["avg_time"], 0)
    
    def test_multiple_calls_statistics(self):
        """Test statistics accumulation over multiple calls."""
        @self.profiler.profile_function()
        def test_function():
            time.sleep(0.001)
            return "test"
        
        # Call function multiple times
        for _ in range(5):
            test_function()
        
        stats = self.profiler.get_function_stats()
        func_name = f"{test_function.__module__}.{test_function.__name__}"
        
        self.assertEqual(stats[func_name]["call_count"], 5)
        self.assertGreater(stats[func_name]["total_time"], 0)
        self.assertGreater(stats[func_name]["avg_time"], 0)
    
    def test_error_handling(self):
        """Test profiling of functions that raise exceptions."""
        @self.profiler.profile_function()
        def failing_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        stats = self.profiler.get_function_stats()
        func_name = f"{failing_function.__module__}.{failing_function.__name__}"
        
        self.assertIn(func_name, stats)
        self.assertEqual(stats[func_name]["errors"], 1)
    
    def test_slowest_functions(self):
        """Test getting slowest functions."""
        @self.profiler.profile_function()
        def slow_function():
            time.sleep(0.02)
        
        @self.profiler.profile_function()
        def fast_function():
            time.sleep(0.001)
        
        slow_function()
        fast_function()
        
        slowest = self.profiler.get_slowest_functions(2)
        self.assertEqual(len(slowest), 2)
        
        # The slow function should be first
        self.assertGreater(slowest[0]["avg_time"], slowest[1]["avg_time"])

class TestExecutionMonitor(unittest.TestCase):
    """Test the execution monitor functionality."""
    
    def setUp(self):
        self.monitor = ExecutionMonitor()
    
    def test_compilation_monitoring(self):
        """Test compilation performance monitoring."""
        @self.monitor.monitor_compilation("python", 1000, lambda: MagicMock(success=True))
        def mock_compile():
            time.sleep(0.01)
            return MagicMock(success=True)
        
        result = mock_compile()
        self.assertTrue(result.success)
        
        # Check language stats
        lang_stats = self.monitor.get_language_performance("python")
        self.assertEqual(lang_stats["compilation_count"], 1)
        self.assertGreater(lang_stats["avg_compilation_time"], 0)
    
    def test_execution_monitoring(self):
        """Test execution performance monitoring."""
        @self.monitor.monitor_execution("python", 5, lambda: MagicMock(passed=5, total=5))
        def mock_execute():
            time.sleep(0.01)
            return MagicMock(passed=5, total=5)
        
        result = mock_execute()
        self.assertEqual(result.passed, 5)
        
        # Check execution stats
        exec_stats = self.monitor.get_execution_performance()
        self.assertIn("python_execution", exec_stats)
        self.assertEqual(exec_stats["python_execution"]["execution_count"], 1)

class TestSimpleCache(unittest.TestCase):
    """Test the simple cache functionality."""
    
    def setUp(self):
        self.cache = SimpleCache(max_size=10, default_ttl=60)
    
    def test_basic_operations(self):
        """Test basic cache operations."""
        # Test set and get
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # Test default value
        self.assertEqual(self.cache.get("nonexistent", "default"), "default")
        
        # Test delete
        self.assertTrue(self.cache.delete("key1"))
        self.assertIsNone(self.cache.get("key1"))
        self.assertFalse(self.cache.delete("key1"))  # Already deleted
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        # Set with short TTL
        self.cache.set("key1", "value1", ttl=1)
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # Wait for expiration
        time.sleep(1.1)
        self.assertIsNone(self.cache.get("key1"))
    
    def test_size_limit(self):
        """Test cache size limits."""
        # Fill cache beyond limit
        for i in range(15):
            self.cache.set(f"key{i}", f"value{i}")
        
        # Should not exceed max size
        stats = self.cache.get_stats()
        self.assertLessEqual(stats["size"], self.cache.max_size)
    
    def test_statistics(self):
        """Test cache statistics."""
        # Generate some hits and misses
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hit_rate"], 50.0)
    
    def test_thread_safety(self):
        """Test thread safety of cache operations."""
        def worker():
            for i in range(100):
                self.cache.set(f"thread_key_{i}", f"value_{i}")
                self.cache.get(f"thread_key_{i}")
        
        # Run multiple threads
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Cache should still be functional
        stats = self.cache.get_stats()
        self.assertGreater(stats["hits"], 0)

class TestFunctionCache(unittest.TestCase):
    """Test the function caching decorator."""
    
    def test_cached_decorator(self):
        """Test the cached decorator functionality."""
        call_count = 0
        
        @cached(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = expensive_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increment
        
        # Different argument should execute function
        result3 = expensive_function(10)
        self.assertEqual(result3, 20)
        self.assertEqual(call_count, 2)

class TestPerformanceOptimizer(unittest.TestCase):
    """Test the performance optimizer functionality."""
    
    def setUp(self):
        self.optimizer = PerformanceOptimizer()
    
    def test_performance_analysis(self):
        """Test performance analysis generation."""
        analysis = self.optimizer.analyze_performance()
        
        self.assertIn("timestamp", analysis)
        self.assertIn("metrics", analysis)
        self.assertIn("issues", analysis)
        self.assertIn("recommendations", analysis)
    
    def test_automatic_optimizations(self):
        """Test automatic optimization application."""
        results = self.optimizer.apply_automatic_optimizations()
        
        self.assertIn("timestamp", results)
        self.assertIn("optimizations_applied", results)
        self.assertIn("errors", results)
        
        # Should have applied cache cleanup
        self.assertGreater(len(results["optimizations_applied"]), 0)
    
    def test_optimization_history(self):
        """Test optimization history tracking."""
        # Apply optimizations
        self.optimizer.apply_automatic_optimizations()
        
        history = self.optimizer.get_optimization_history()
        self.assertEqual(len(history), 1)
        self.assertIn("timestamp", history[0])

if __name__ == "__main__":
    unittest.main()