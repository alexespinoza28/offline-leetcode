"""
Enhanced execution service with integrated performance monitoring.
This module extends the existing execution service with comprehensive
performance monitoring and optimization capabilities.
"""
import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from ..execution.service import ExecutionService
    from .profiler import profile
    from .monitor import execution_monitor, monitor_compilation, monitor_execution
    from .cache import cache_problem_data, cache_results
    from .optimizer import analyze_performance, get_recommendations
except ImportError:
    from execution.service import ExecutionService
    from performance.profiler import profile
    from performance.monitor import execution_monitor, monitor_compilation, monitor_execution
    from performance.cache import cache_problem_data, cache_results
    from performance.optimizer import analyze_performance, get_recommendations

logger = logging.getLogger(__name__)

class EnhancedExecutionService(ExecutionService):
    """
    Enhanced execution service with integrated performance monitoring.
    
    This service extends the base ExecutionService with:
    - Comprehensive performance profiling
    - Execution monitoring and analytics
    - Intelligent caching strategies
    - Automatic performance optimization
    - Detailed performance reporting
    """
    
    def __init__(self, work_dir: str = "/tmp/code_execution"):
        super().__init__(work_dir)
        self.performance_enabled = True
        self.cache_enabled = True
        
        # Performance tracking
        self.performance_stats = {
            "total_execution_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "optimizations_applied": 0
        }
    
    @profile(include_memory=True, include_cpu=True)
    async def execute_solution(
        self,
        code: str,
        language: str,
        problem_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a solution with comprehensive performance monitoring."""
        
        start_time = time.perf_counter()
        
        try:
            # Check cache first if enabled
            if self.cache_enabled:
                cached_result = await self._get_cached_result(code, language, problem_id)
                if cached_result:
                    self.performance_stats["cache_hits"] += 1
                    cached_result["from_cache"] = True
                    cached_result["execution_time_ms"] = (time.perf_counter() - start_time) * 1000
                    return cached_result
                else:
                    self.performance_stats["cache_misses"] += 1
            
            # Monitor compilation if applicable
            code_size = len(code.encode('utf-8'))
            
            @monitor_compilation(language, code_size)
            def compile_code():
                # This would be the actual compilation step
                return type('CompileResult', (), {'success': True, 'output': '', 'errors': ''})()
            
            # Execute with monitoring
            @monitor_execution(language, 0)  # Test count will be updated later
            async def execute_with_monitoring():
                return await super(EnhancedExecutionService, self).execute_solution(
                    code, language, problem_id, user_id, session_id
                )
            
            # Perform execution
            result = await execute_with_monitoring()
            
            # Update test count in monitoring
            test_count = result.get("total_tests", 0)
            execution_monitor.execution_stats[f"{language}_execution"]["total_tests_run"] += test_count
            
            # Cache successful results
            if self.cache_enabled and result.get("status") != "error":
                await self._cache_result(code, language, problem_id, result)
            
            # Add performance metrics to result
            execution_time = (time.perf_counter() - start_time) * 1000
            result["performance_metrics"] = {
                "total_execution_time_ms": execution_time,
                "from_cache": False,
                "language_stats": execution_monitor.get_language_performance(language),
                "system_performance": self._get_current_system_metrics()
            }
            
            # Update performance stats
            self.performance_stats["total_execution_time"] += execution_time
            
            # Check for optimization opportunities
            await self._check_optimization_opportunities(result)
            
            return result
            
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Enhanced execution error: {e}")
            
            return {
                "status": "error",
                "message": f"Enhanced execution error: {str(e)}",
                "performance_metrics": {
                    "total_execution_time_ms": execution_time,
                    "from_cache": False,
                    "error": str(e)
                }
            }
    
    @cache_problem_data(ttl=3600)  # Cache for 1 hour
    async def _load_test_cases(self, problem_id: str):
        """Load test cases with caching."""
        return await super()._load_test_cases(problem_id)
    
    @cache_results(ttl=900)  # Cache for 15 minutes
    async def _get_cached_result(self, code: str, language: str, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get cached execution result if available."""
        # This is a placeholder - in a real implementation, you'd use a proper cache key
        # that considers code content, language, and problem
        cache_key = f"{problem_id}_{language}_{hash(code)}"
        # The actual caching is handled by the decorator
        return None  # Will be replaced by cached decorator
    
    async def _cache_result(self, code: str, language: str, problem_id: str, result: Dict[str, Any]):
        """Cache execution result for future use."""
        # This would store the result in cache
        # Implementation depends on your caching strategy
        pass
    
    def _get_current_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {"error": "psutil not available"}
    
    async def _check_optimization_opportunities(self, result: Dict[str, Any]):
        """Check for performance optimization opportunities."""
        try:
            # Get current performance analysis
            analysis = analyze_performance()
            
            # Check if we have high-priority recommendations
            recommendations = analysis.get("recommendations", [])
            high_priority_recs = [r for r in recommendations if r.priority == "high"]
            
            if high_priority_recs:
                logger.info(f"Found {len(high_priority_recs)} high-priority optimization opportunities")
                
                # Add recommendations to result
                result["optimization_recommendations"] = [
                    {
                        "title": rec.title,
                        "description": rec.description,
                        "impact": rec.impact,
                        "implementation": rec.implementation
                    }
                    for rec in high_priority_recs[:3]  # Limit to top 3
                ]
        
        except Exception as e:
            logger.error(f"Error checking optimization opportunities: {e}")
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        try:
            # Get base execution stats
            base_stats = await super().get_execution_stats()
            
            # Get performance analysis
            performance_analysis = analyze_performance()
            
            # Get monitoring summary
            monitoring_summary = execution_monitor.get_performance_summary()
            
            # Combine all metrics
            report = {
                "timestamp": performance_analysis["timestamp"],
                "execution_stats": base_stats,
                "performance_analysis": performance_analysis,
                "monitoring_summary": monitoring_summary,
                "enhanced_stats": self.performance_stats,
                "system_health": self._get_system_health_status(),
                "recommendations": get_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {
                "error": f"Failed to generate performance report: {str(e)}",
                "timestamp": time.time()
            }
    
    def _get_system_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Calculate cache efficiency
            total_cache_requests = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
            cache_hit_rate = (
                self.performance_stats["cache_hits"] / total_cache_requests * 100
                if total_cache_requests > 0 else 0
            )
            
            # Determine health status
            health_score = 100
            status = "excellent"
            
            if cache_hit_rate < 70:
                health_score -= 20
                status = "good"
            
            if cache_hit_rate < 50:
                health_score -= 30
                status = "fair"
            
            if cache_hit_rate < 30:
                health_score -= 50
                status = "poor"
            
            return {
                "overall_status": status,
                "health_score": max(0, health_score),
                "cache_hit_rate": cache_hit_rate,
                "total_executions": self.stats["total_executions"],
                "average_execution_time": self.performance_stats["total_execution_time"] / max(1, self.stats["total_executions"])
            }
            
        except Exception as e:
            logger.error(f"Error calculating system health: {e}")
            return {
                "overall_status": "unknown",
                "health_score": 0,
                "error": str(e)
            }
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Apply automatic performance optimizations."""
        try:
            from .optimizer import apply_optimizations
            
            optimization_results = apply_optimizations()
            self.performance_stats["optimizations_applied"] += len(
                optimization_results.get("optimizations_applied", [])
            )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
            return {
                "error": f"Failed to apply optimizations: {str(e)}",
                "optimizations_applied": [],
                "errors": [str(e)]
            }
    
    def enable_performance_monitoring(self, enabled: bool = True):
        """Enable or disable performance monitoring."""
        self.performance_enabled = enabled
        logger.info(f"Performance monitoring {'enabled' if enabled else 'disabled'}")
    
    def enable_caching(self, enabled: bool = True):
        """Enable or disable result caching."""
        self.cache_enabled = enabled
        logger.info(f"Result caching {'enabled' if enabled else 'disabled'}")

# Global enhanced execution service instance
enhanced_execution_service = EnhancedExecutionService()