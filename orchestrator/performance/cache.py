"""
Simple caching system for the Interview Coding Platform.
This module provides basic caching functionality to improve performance
by reducing redundant computations and file I/O operations.
"""
import time
import hashlib
import threading
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """
    Thread-safe in-memory cache with TTL support.
    Features:
    - TTL (Time To Live) support
    - Maximum size limits
    - Thread safety
    - Access statistics
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def _generate_key(self, key: Any) -> str:
        """Generate a string key from various input types."""
        if isinstance(key, str):
            return key
        else:
            return hashlib.md5(str(key).encode()).hexdigest()
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if a cache entry has expired."""
        if "expires_at" not in entry or entry["expires_at"] is None:
            return False
        return datetime.now() > entry["expires_at"]
    
    def _evict_expired(self):
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if self._is_expired(entry)
        ]
        for key in expired_keys:
            del self._cache[key]
            self._stats["evictions"] += 1
    
    def _evict_oldest(self):
        """Evict oldest entries when cache is full."""
        if len(self._cache) <= self.max_size:
            return
        
        # Sort by creation time (oldest first)
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1]["created_at"]
        )
        
        # Remove oldest entries until we're under the limit
        entries_to_remove = len(self._cache) - self.max_size + 1
        for i in range(entries_to_remove):
            key, _ = sorted_entries[i]
            del self._cache[key]
            self._stats["evictions"] += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get a value from the cache."""
        str_key = self._generate_key(key)
        
        with self._lock:
            self._evict_expired()
            
            if str_key not in self._cache:
                self._stats["misses"] += 1
                return default
            
            entry = self._cache[str_key]
            if self._is_expired(entry):
                del self._cache[str_key]
                self._stats["misses"] += 1
                self._stats["evictions"] += 1
                return default
            
            # Update access time
            entry["last_accessed"] = datetime.now()
            self._stats["hits"] += 1
            return entry["value"]
    
    def set(self, key: Any, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache."""
        str_key = self._generate_key(key)
        ttl = ttl or self.default_ttl
        
        with self._lock:
            self._evict_expired()
            self._evict_oldest()
            
            # Calculate expiration time
            expires_at = None
            if ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # Create cache entry
            entry = {
                "value": value,
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "expires_at": expires_at
            }
            
            self._cache[str_key] = entry
            return True
    
    def delete(self, key: Any) -> bool:
        """Delete a value from the cache."""
        str_key = self._generate_key(key)
        
        with self._lock:
            if str_key in self._cache:
                del self._cache[str_key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._stats["evictions"] += len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                self._stats["hits"] / total_requests * 100
                if total_requests > 0 else 0
            )
            
            return {
                **self._stats,
                "size": len(self._cache),
                "hit_rate": hit_rate,
                "max_size": self.max_size
            }

class FunctionCache:
    """
    Decorator-based function result caching.
    Automatically caches function results based on arguments.
    """
    
    def __init__(self, cache: Optional[SimpleCache] = None, ttl: int = 3600):
        self.cache = cache or SimpleCache()
        self.ttl = ttl
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = (func.__name__, args, tuple(sorted(kwargs.items())))
            cache_key = hashlib.md5(str(key_data).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache.set(cache_key, result, self.ttl)
            return result
        
        # Add cache management methods to the wrapper
        wrapper.cache_clear = lambda: self.cache.clear()
        wrapper.cache_info = lambda: self.cache.get_stats()
        return wrapper

# Global cache instances
default_cache = SimpleCache(max_size=500, default_ttl=1800)  # 30 minutes
problem_cache = SimpleCache(max_size=100, default_ttl=3600)  # 1 hour for problem data
result_cache = SimpleCache(max_size=200, default_ttl=900)    # 15 minutes for results

def cached(ttl: int = 3600, cache: Optional[SimpleCache] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        cache: Cache instance to use (defaults to global cache)
    """
    return FunctionCache(cache or default_cache, ttl)

def cache_problem_data(ttl: int = 3600):
    """Decorator specifically for caching problem-related data."""
    return FunctionCache(problem_cache, ttl)

def cache_results(ttl: int = 900):
    """Decorator specifically for caching execution results."""
    return FunctionCache(result_cache, ttl)

def get_cache_stats() -> Dict[str, Any]:
    """Get statistics for all cache instances."""
    return {
        "default_cache": default_cache.get_stats(),
        "problem_cache": problem_cache.get_stats(),
        "result_cache": result_cache.get_stats()
    }

def clear_all_caches():
    """Clear all cache instances."""
    default_cache.clear()
    problem_cache.clear()
    result_cache.clear()
    logger.info("All caches cleared")