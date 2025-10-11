# Quick Start: Using Caching in CourseWagon

## For Backend Developers (Python)

### Using Cache in Services

```python
from utils.cache_helper import cache_helper, invalidate_cache

# 1. Cache a method result
def get_user_data(user_id):
    cache_key = f"user:{user_id}"
    
    # Try to get from cache
    cached = cache_helper.get(cache_key)
    if cached is not None:
        return cached
    
    # Cache miss - fetch from database
    data = fetch_from_database(user_id)
    
    # Store in cache with 5 minute TTL
    cache_helper.set(cache_key, data, ttl=300)
    return data

# 2. Using decorator (easiest way)
from utils.cache_helper import cached

@cached(ttl=600, key_prefix="course")
def get_expensive_data(course_id):
    return expensive_database_query(course_id)

# 3. Invalidate cache after updates
def update_course(course_id, data):
    # Update database
    course = update_in_db(course_id, data)
    
    # Invalidate caches
    invalidate_cache(f"course:{course_id}")
    invalidate_cache(f"courses:user:{course.user_id}")
    
    return course
```

### Common Cache Keys
- User: `user:{user_id}`, `user:{user_id}:{resource}`
- Course: `course:{id}`, `courses:all`, `courses:user:{user_id}`
- Subject: `subject:{id}`, `subjects:course:{course_id}`
- Topic: `topic:{id}`, `topics:chapter:{chapter_id}`
- Content: `content:topic:{topic_id}`

### TTL Guidelines
- Frequently changing data: 1-3 minutes
- Stable lists: 5 minutes
- Expensive computations: 10+ minutes
- Static data: 30+ minutes

## For Frontend Developers (Angular)

### Using Cache Service

```typescript
import { CacheService } from './services/cache.service';

constructor(private cacheService: CacheService) {}

// 1. Memory cache (fast, not persistent)
saveToCache() {
  const data = { id: 1, name: 'Course' };
  this.cacheService.set('course:1', data, 5 * 60 * 1000); // 5 min TTL
}

getFromCache() {
  const data = this.cacheService.get('course:1');
  return data;
}

// 2. LocalStorage cache (persistent across sessions)
saveToLocalStorage() {
  const preferences = { theme: 'dark' };
  this.cacheService.setLocal('user:preferences', preferences, 60); // 60 min TTL
}

// 3. Invalidate cache after mutations
updateCourse(courseId: number, data: any) {
  return this.http.put(`/api/courses/${courseId}`, data).pipe(
    tap(() => {
      // Clear related caches
      this.cacheService.invalidate('courses:');
      this.cacheService.delete(`course:${courseId}`);
    })
  );
}
```

### Using Observable Caching (Request Deduplication)

```typescript
import { shareReplay } from 'rxjs/operators';

private requestCache = new Map<number, Observable<any>>();

getCourseDetails(courseId: number): Observable<any> {
  // Check if request is already in flight
  if (this.requestCache.has(courseId)) {
    return this.requestCache.get(courseId)!;
  }
  
  // Make new request
  const request$ = this.http.get(`/api/courses/${courseId}`).pipe(
    shareReplay(1),  // Share result with all subscribers
    tap(() => this.requestCache.delete(courseId))
  );
  
  this.requestCache.set(courseId, request$);
  return request$;
}
```

### Skip HTTP Cache for Specific Requests

```typescript
import { HttpHeaders } from '@angular/common/http';

// Force fresh data (bypass cache interceptor)
const headers = new HttpHeaders({ 'X-Skip-Cache': 'true' });
this.http.get(url, { headers });
```

## Cache Management

### Check Cache Statistics

**Backend (Python):**
```python
# Check if using Redis or memory cache
from utils.cache_helper import cache_helper
print(f"Using Redis: {cache_helper.use_redis}")
```

**Frontend (TypeScript):**
```typescript
const stats = this.cacheService.getCacheStats();
console.log(`Memory: ${stats.memorySize}, LocalStorage: ${stats.localStorageKeys}`);
```

### Clear All Cache

**Backend:**
```python
from utils.cache_helper import cache_helper
cache_helper.clear_all()
```

**Frontend:**
```typescript
this.cacheService.clear();  // Clear memory cache
// LocalStorage cache cleared automatically or manually per key
```

## Common Patterns

### 1. List + Detail Pattern
```python
# List endpoint - shorter TTL
@cached(ttl=180, key_prefix="courses:user")
def get_user_courses(user_id):
    return query_user_courses(user_id)

# Detail endpoint - longer TTL
@cached(ttl=300, key_prefix="course")
def get_course_details(course_id):
    return query_course(course_id)
```

### 2. Stale While Revalidate (Frontend)
```typescript
getData(id: number, forceRefresh = false): Observable<any> {
  const cacheKey = `data:${id}`;
  
  if (!forceRefresh) {
    const cached = this.cacheService.get(cacheKey);
    if (cached) {
      // Return cached immediately
      setTimeout(() => {
        // Refresh in background
        this.fetchFreshData(id).subscribe(fresh => {
          this.cacheService.set(cacheKey, fresh);
        });
      }, 0);
      return of(cached);
    }
  }
  
  return this.fetchFreshData(id);
}
```

### 3. Hierarchical Invalidation
```python
# When updating a course, invalidate all related caches
def update_course(course_id, data):
    course = update_in_db(course_id, data)
    
    # Invalidate specific course
    cache_helper.delete(f"course:{course_id}")
    
    # Invalidate user's course list
    invalidate_cache(f"courses:user:{course.user_id}")
    
    # Invalidate all courses list
    invalidate_cache("courses:all")
    
    # Invalidate related subjects
    invalidate_cache(f"subjects:course:{course_id}")
    
    return course
```

## Testing

### Test with Cache Enabled
```python
# Backend
def test_cache_works():
    # First call - cache miss
    result1 = service.get_data(123)
    
    # Second call - cache hit (should be faster)
    result2 = service.get_data(123)
    
    assert result1 == result2
```

### Test Cache Invalidation
```python
def test_cache_invalidates():
    # Get initial data
    data1 = service.get_data(123)
    
    # Update data
    service.update_data(123, new_data)
    
    # Should get fresh data (not cached)
    data2 = service.get_data(123)
    
    assert data2 == new_data
```

## Troubleshooting

### Cache Not Working
1. Check Redis connection (backend)
2. Check browser console for errors (frontend)
3. Verify cache keys are consistent
4. Check TTL values aren't too short

### Stale Data
1. Verify cache invalidation on updates
2. Reduce TTL for frequently changing data
3. Add manual refresh option
4. Check invalidation patterns

### Performance Not Improved
1. Monitor cache hit ratio
2. Increase TTL if hit ratio is low
3. Check if cache keys are unique
4. Verify data is actually being cached

## Best Practices

✅ **DO:**
- Use descriptive, hierarchical cache keys
- Set appropriate TTL based on data change frequency
- Invalidate related caches together
- Log cache hits/misses during development
- Test cache invalidation

❌ **DON'T:**
- Cache user-sensitive data without encryption
- Set very long TTL for frequently changing data
- Forget to invalidate cache after updates
- Cache large objects (>1MB)
- Share cache keys across different data types

## Additional Resources

- Full Documentation: `/python-server/docs/CACHING_OPTIMIZATION.md`
- Implementation Summary: `/PERFORMANCE_OPTIMIZATION_SUMMARY.md`
- Cache Tests: `/python-server/tests/test_cache.py`
- Cache Service Tests: `/angular-client/src/app/services/cache.service.spec.ts`
