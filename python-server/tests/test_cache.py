# tests/test_cache.py
"""
Tests for cache functionality
"""
import pytest
import time
from utils.cache_helper import CacheHelper, cache_helper, cached, invalidate_cache

def test_cache_set_and_get():
    """Test basic cache set and get operations"""
    cache = CacheHelper()
    
    # Test set and get
    cache.set("test_key", "test_value", ttl=60)
    result = cache.get("test_key")
    assert result == "test_value"

def test_cache_expiration():
    """Test cache TTL expiration"""
    cache = CacheHelper()
    
    # Set with short TTL
    cache.set("expiring_key", "expiring_value", ttl=1)
    
    # Should be available immediately
    result = cache.get("expiring_key")
    assert result == "expiring_value"
    
    # Wait for expiration
    time.sleep(2)
    
    # Should be None after expiration
    result = cache.get("expiring_key")
    assert result is None

def test_cache_delete():
    """Test cache deletion"""
    cache = CacheHelper()
    
    cache.set("delete_key", "delete_value", ttl=60)
    assert cache.get("delete_key") == "delete_value"
    
    cache.delete("delete_key")
    assert cache.get("delete_key") is None

def test_cache_pattern_delete():
    """Test pattern-based cache deletion"""
    cache = CacheHelper()
    
    # Set multiple keys with pattern
    cache.set("user:1:profile", {"name": "User 1"}, ttl=60)
    cache.set("user:1:settings", {"theme": "dark"}, ttl=60)
    cache.set("user:2:profile", {"name": "User 2"}, ttl=60)
    cache.set("course:1", {"name": "Course 1"}, ttl=60)
    
    # Delete all user:1: keys
    count = cache.delete_pattern("user:1:*")
    assert count == 2
    
    # user:1 keys should be gone
    assert cache.get("user:1:profile") is None
    assert cache.get("user:1:settings") is None
    
    # Other keys should still exist
    assert cache.get("user:2:profile") is not None
    assert cache.get("course:1") is not None

def test_cache_complex_data():
    """Test caching complex data structures"""
    cache = CacheHelper()
    
    # Test with dict
    data = {
        "id": 1,
        "name": "Test Course",
        "subjects": [
            {"id": 1, "name": "Subject 1"},
            {"id": 2, "name": "Subject 2"}
        ]
    }
    
    cache.set("complex_key", data, ttl=60)
    result = cache.get("complex_key")
    
    assert result == data
    assert result["name"] == "Test Course"
    assert len(result["subjects"]) == 2

def test_cached_decorator():
    """Test the @cached decorator"""
    call_count = [0]
    
    @cached(ttl=60, key_prefix="test")
    def expensive_function(x, y):
        call_count[0] += 1
        return x + y
    
    # First call should execute the function
    result1 = expensive_function(1, 2)
    assert result1 == 3
    assert call_count[0] == 1
    
    # Second call with same args should use cache
    result2 = expensive_function(1, 2)
    assert result2 == 3
    assert call_count[0] == 1  # Should not increment
    
    # Call with different args should execute again
    result3 = expensive_function(2, 3)
    assert result3 == 5
    assert call_count[0] == 2

def test_invalidate_cache_function():
    """Test the invalidate_cache helper function"""
    # Set some test data
    cache_helper.set("courses:all", [1, 2, 3], ttl=60)
    cache_helper.set("courses:user:1", [1, 2], ttl=60)
    cache_helper.set("user:1:profile", {"name": "Test"}, ttl=60)
    
    # Invalidate courses
    count = invalidate_cache("courses:*")
    assert count >= 2
    
    # Courses should be gone
    assert cache_helper.get("courses:all") is None
    assert cache_helper.get("courses:user:1") is None
    
    # User profile should still exist
    assert cache_helper.get("user:1:profile") is not None

def test_cache_none_value():
    """Test that None values are handled correctly"""
    cache = CacheHelper()
    
    # None values should not be cached by default
    result = cache.get("nonexistent_key")
    assert result is None

def test_cache_global_instance():
    """Test that the global cache_helper instance works"""
    # Test with global instance
    cache_helper.set("global_test", "global_value", ttl=60)
    result = cache_helper.get("global_test")
    assert result == "global_value"
    
    # Clean up
    cache_helper.delete("global_test")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
