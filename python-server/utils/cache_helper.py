# utils/cache_helper.py
"""
Redis-based caching utility with Upstash Redis (REST) as primary,
falling back to standard Redis, then in-memory cache.
"""
import os
import json
import logging
import functools
import fnmatch
import time
from typing import Optional, Callable, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# In-memory cache as final fallback
_memory_cache: dict = {}
_memory_cache_timestamps: dict = {}


class CacheHelper:
    """
    Cache helper — tries Upstash Redis (REST) first, then standard Redis,
    then falls back to in-memory cache.
    """

    def __init__(self):
        self.redis_client = None
        self.use_redis = False
        self._try_upstash() or self._try_standard_redis()
        if not self.use_redis:
            logger.info("Using in-memory cache (not persistent)")

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def _try_upstash(self) -> bool:
        url = os.environ.get("UPSTASH_REDIS_REST_URL")
        token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
        if not url or not token:
            return False
        try:
            from upstash_redis import Redis
            client = Redis(url=url, token=token)
            client.ping()
            self.redis_client = client
            self.use_redis = True
            self._is_upstash = True
            logger.info(f"Upstash Redis connected: {url}")
            return True
        except Exception as e:
            logger.warning(f"Upstash Redis connection failed: {e}")
            return False

    def _try_standard_redis(self) -> bool:
        try:
            import redis
            client = redis.Redis(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=int(os.environ.get("REDIS_PORT", "6379")),
                db=int(os.environ.get("REDIS_DB", "0")),
                password=os.environ.get("REDIS_PASSWORD") or None,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            client.ping()
            self.redis_client = client
            self.use_redis = True
            self._is_upstash = False
            logger.info(f"Redis connected: {os.environ.get('REDIS_HOST', 'localhost')}")
            return True
        except Exception as e:
            logger.warning(f"Standard Redis connection failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def _serialize(self, value: Any) -> str:
        try:
            return json.dumps(value, default=str)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return None

    def _deserialize(self, value: str) -> Any:
        try:
            return json.loads(value)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None

    # ------------------------------------------------------------------
    # Core cache operations
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        try:
            if self.use_redis and self.redis_client:
                value = self.redis_client.get(key)
                if value is not None:
                    return self._deserialize(value)
            else:
                if key in _memory_cache:
                    expiry = _memory_cache_timestamps.get(key, 0)
                    if expiry == 0 or time.time() < expiry:
                        return _memory_cache[key]
                    _memory_cache.pop(key, None)
                    _memory_cache_timestamps.pop(key, None)
        except Exception as e:
            logger.error(f"Cache get error [{key}]: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        try:
            if self.use_redis and self.redis_client:
                serialized = self._serialize(value)
                if serialized is None:
                    return False
                # Both upstash_redis and redis-py accept set(key, value, ex=ttl)
                self.redis_client.set(key, serialized, ex=ttl)
                return True
            else:
                _memory_cache[key] = value
                _memory_cache_timestamps[key] = time.time() + ttl
                return True
        except Exception as e:
            logger.error(f"Cache set error [{key}]: {e}")
        return False

    def delete(self, key: str) -> bool:
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                _memory_cache.pop(key, None)
                _memory_cache_timestamps.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error [{key}]: {e}")
        return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern (e.g. 'courses:*')."""
        count = 0
        try:
            if self.use_redis and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            else:
                to_delete = [k for k in _memory_cache if fnmatch.fnmatch(k, pattern)]
                for k in to_delete:
                    _memory_cache.pop(k, None)
                    _memory_cache_timestamps.pop(k, None)
                count = len(to_delete)
        except Exception as e:
            logger.error(f"Cache delete_pattern error [{pattern}]: {e}")
        return count

    def clear_all(self) -> bool:
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.flushdb()
            else:
                _memory_cache.clear()
                _memory_cache_timestamps.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear_all error: {e}")
            return False

    @property
    def backend(self) -> str:
        if not self.use_redis:
            return "memory"
        return "upstash" if getattr(self, "_is_upstash", False) else "redis"


# Global singleton
cache_helper = CacheHelper()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Usage:
        @cached(ttl=600, key_prefix="course")
        def get_course(course_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            prefix = key_prefix or func.__name__
            parts = [prefix] + [str(a) for a in args]
            parts += [f"{k}:{v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(parts)

            cached_value = cache_helper.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit [{cache_key}]")
                return cached_value

            logger.debug(f"Cache miss [{cache_key}]")
            result = func(*args, **kwargs)
            if result is not None:
                cache_helper.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching a glob pattern."""
    count = cache_helper.delete_pattern(pattern)
    logger.info(f"Invalidated {count} cache entries matching: {pattern}")
    return count
