# utils/cache_helper.py
"""
Redis-based caching utility with fallback to in-memory cache.
Provides decorator for caching function results with TTL support.
"""
import os
import json
import logging
import functools
from typing import Optional, Callable, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

# Try to import redis, but don't fail if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache fallback")

# In-memory cache as fallback
_memory_cache = {}
_memory_cache_timestamps = {}

class CacheHelper:
    """
    Cache helper with Redis support and in-memory fallback.
    Handles serialization/deserialization of Python objects.
    """
    
    def __init__(self):
        self.redis_client = None
        self.use_redis = False
        
        if REDIS_AVAILABLE:
            try:
                redis_host = os.environ.get('REDIS_HOST', 'localhost')
                redis_port = int(os.environ.get('REDIS_PORT', '6379'))
                redis_db = int(os.environ.get('REDIS_DB', '0'))
                redis_password = os.environ.get('REDIS_PASSWORD', None)
                
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                logger.info(f"Redis cache initialized at {redis_host}:{redis_port}")
                
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory cache: {str(e)}")
                self.redis_client = None
                self.use_redis = False
        
        if not self.use_redis:
            logger.info("Using in-memory cache (not persistent)")
    
    def _serialize(self, value: Any) -> str:
        """Serialize Python object to JSON string"""
        try:
            return json.dumps(value, default=str)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return None
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize JSON string to Python object"""
        try:
            return json.loads(value)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.use_redis and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return self._deserialize(value)
            else:
                # Memory cache with TTL check
                if key in _memory_cache:
                    import time
                    timestamp = _memory_cache_timestamps.get(key, 0)
                    # Check if expired (stored as unix timestamp + ttl)
                    if timestamp == 0 or time.time() < timestamp:
                        return _memory_cache[key]
                    else:
                        # Expired, remove from cache
                        del _memory_cache[key]
                        del _memory_cache_timestamps[key]
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default 300 = 5 minutes)
        """
        try:
            if self.use_redis and self.redis_client:
                serialized = self._serialize(value)
                if serialized:
                    self.redis_client.setex(key, ttl, serialized)
                    return True
            else:
                # Memory cache
                import time
                _memory_cache[key] = value
                # Store expiration time
                _memory_cache_timestamps[key] = time.time() + ttl
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
        
        return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
                return True
            else:
                if key in _memory_cache:
                    del _memory_cache[key]
                if key in _memory_cache_timestamps:
                    del _memory_cache_timestamps[key]
                return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
        
        return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Pattern to match (e.g., "user:*", "courses:*")
        
        Returns:
            Number of keys deleted
        """
        count = 0
        try:
            if self.use_redis and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            else:
                # Memory cache pattern matching
                import fnmatch
                keys_to_delete = [k for k in _memory_cache.keys() if fnmatch.fnmatch(k, pattern)]
                for key in keys_to_delete:
                    del _memory_cache[key]
                    if key in _memory_cache_timestamps:
                        del _memory_cache_timestamps[key]
                count = len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
        
        return count
    
    def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.flushdb()
            else:
                _memory_cache.clear()
                _memory_cache_timestamps.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False

# Global cache instance
cache_helper = CacheHelper()

def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (default 300 = 5 minutes)
        key_prefix: Prefix for cache key (default uses function name)
    
    Usage:
        @cached(ttl=600, key_prefix="user")
        def get_user_by_id(user_id):
            # expensive operation
            return user_data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            prefix = key_prefix or func.__name__
            
            # Create a simple key from args and kwargs
            key_parts = [str(prefix)]
            if args:
                key_parts.extend([str(arg) for arg in args])
            if kwargs:
                key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache_helper.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Cache miss, call function
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                cache_helper.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """
    Helper function to invalidate cache by pattern
    
    Usage:
        invalidate_cache("courses:*")
        invalidate_cache("user:123:*")
    """
    count = cache_helper.delete_pattern(pattern)
    logger.info(f"Invalidated {count} cache entries matching pattern: {pattern}")
    return count
