# Caching and Performance Optimization Documentation

## Overview

This document describes the caching strategy and performance optimizations implemented in CourseWagon.

## Caching Architecture

### Backend Caching (Python)

The backend uses a two-tier caching approach:
1. **Redis Cache** (primary) - Fast, shared across instances
2. **In-Memory Cache** (fallback) - When Redis is unavailable

#### Cache Helper (`utils/cache_helper.py`)

The `CacheHelper` class provides:
- Automatic Redis/memory cache selection
- JSON serialization for Python objects
- TTL (Time-To-Live) support
- Pattern-based cache invalidation
- Decorator for easy caching

**Usage Example:**
```python
from utils.cache_helper import cache_helper, cached, invalidate_cache

# Direct cache usage
cache_helper.set("user:123", user_data, ttl=300)  # 5 minutes
data = cache_helper.get("user:123")

# Using decorator
@cached(ttl=600, key_prefix="course")
def get_expensive_data(course_id):
    return expensive_database_query(course_id)

# Invalidate cache
invalidate_cache("courses:*")  # Invalidate all course-related cache
```

#### Cache Keys Convention

- **Courses**: `course:{id}`, `courses:all`, `courses:user:{user_id}`
- **Subjects**: `subject:{id}`, `subjects:course:{course_id}`
- **Topics**: `topic:{id}`, `topics:subject:{subject_id}`
- **Content**: `content:{id}`, `content:topic:{topic_id}`

#### TTL Settings

- Course list: 5 minutes (300s)
- User courses: 3 minutes (180s)
- Individual resources: 5 minutes (300s)
- Subjects/Topics: 5 minutes (300s)

### Frontend Caching (Angular)

The frontend implements multi-level caching:

1. **HTTP Interceptor Cache** - Automatic GET request caching
2. **Memory Cache Service** - Fast in-memory caching
3. **LocalStorage Cache** - Persistent cross-session caching
4. **Observable Cache** - Request deduplication with `shareReplay`

#### Cache Service (`services/cache.service.ts`)

**Usage Example:**
```typescript
// Inject the service
constructor(private cacheService: CacheService) {}

// Memory cache
this.cacheService.set('user:profile', userData, 5 * 60 * 1000);
const data = this.cacheService.get('user:profile');

// LocalStorage cache (persistent)
this.cacheService.setLocal('preferences', prefs, 60); // 60 minutes

// Invalidate cache
this.cacheService.invalidate('courses:');  // Pattern-based
```

#### HTTP Cache Interceptor

Automatically caches GET requests for 3 minutes.

To skip cache for specific requests:
```typescript
const headers = new HttpHeaders({ 'X-Skip-Cache': 'true' });
this.http.get(url, { headers });
```

#### Observable Caching with shareReplay

Prevents duplicate HTTP requests for the same resource:
```typescript
getCourseDetails(courseId: number): Observable<any> {
  // Check if request is already in flight
  if (this.courseDetailsCache.has(courseId)) {
    return this.courseDetailsCache.get(courseId)!;
  }
  
  const request$ = this.http.get(`${this.apiUrl}/${courseId}`).pipe(
    shareReplay(1),  // Share with multiple subscribers
    tap(() => this.courseDetailsCache.delete(courseId))
  );
  
  this.courseDetailsCache.set(courseId, request$);
  return request$;
}
```

## Cache Invalidation Strategy

### Automatic Invalidation

Caches are automatically invalidated on:
- **Create**: Invalidate list caches
- **Update**: Invalidate specific item and related list caches
- **Delete**: Invalidate specific item and related list caches

### Manual Invalidation

When data changes through external means, manually invalidate:

**Backend:**
```python
from utils.cache_helper import invalidate_cache

# After bulk operation
invalidate_cache("courses:*")
```

**Frontend:**
```typescript
this.cacheService.invalidate('courses:');
this.cacheService.clear();  // Clear all memory cache
```

## Database Optimization

### Connection Pooling

Configured in `extensions.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Base pool size
    max_overflow=30,        # Additional connections allowed
    pool_pre_ping=True,     # Check connection before use
    pool_recycle=3600,      # Recycle connections every hour
    pool_timeout=30         # Timeout for getting connection
)
```

### Query Optimization

1. **Eager Loading**: Use `joinedload` to prevent N+1 queries
```python
from sqlalchemy.orm import joinedload

courses = db.query(Course).options(
    joinedload(Course.subjects).joinedload(Subject.topics)
).all()
```

2. **Selective Fields**: Query only needed columns
```python
results = db.query(Course.id, Course.name).all()
```

3. **Pagination**: Limit results
```python
query.offset(offset).limit(limit).all()
```

## Performance Monitoring

### Cache Hit Ratio

Monitor cache effectiveness:
```python
# Backend: Log cache hits/misses
logger.debug(f"Cache hit for {cache_key}")
logger.debug(f"Cache miss for {cache_key}")
```

```typescript
// Frontend: Console logs
console.log(`[Cache] Hit: ${url}`);
console.log(`[Cache] Miss: ${url}`);
```

### Cache Statistics

```typescript
// Get cache statistics
const stats = this.cacheService.getCacheStats();
console.log(`Memory cache size: ${stats.memorySize}`);
console.log(`LocalStorage keys: ${stats.localStorageKeys}`);
```

## Configuration

### Redis Configuration (Backend)

Environment variables:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password  # Optional
```

If Redis is not configured, the system automatically falls back to in-memory caching.

### Cache TTL Configuration

Adjust TTL values in service files:
```python
cache_helper.set(key, value, ttl=600)  # 10 minutes
```

```typescript
this.cacheService.set(key, value, 10 * 60 * 1000);  // 10 minutes
```

## Best Practices

1. **Cache Immutable Data Longer**: Static content can have longer TTL
2. **Invalidate Aggressively**: When in doubt, invalidate related caches
3. **Use Pattern Matching**: Invalidate groups of related keys
4. **Monitor Cache Size**: Clear old entries in LocalStorage
5. **Test Without Cache**: Ensure functionality works without cache
6. **Log Cache Operations**: Monitor hit/miss ratio for optimization

## Testing

### Backend Cache Tests

```bash
cd python-server
python -m pytest tests/test_cache.py -v
```

### Frontend Cache Tests

```bash
cd angular-client
npm test -- --include='**/cache.service.spec.ts'
```

## Troubleshooting

### Cache Not Working

1. Check Redis connection (backend)
2. Check browser LocalStorage quota (frontend)
3. Verify cache keys are consistent
4. Check TTL values are not too short

### Stale Data

1. Verify cache invalidation on updates
2. Reduce TTL for frequently changing data
3. Add manual cache clearing option for users

### Performance Issues

1. Monitor cache hit ratio
2. Increase TTL for stable data
3. Implement cache warming for critical paths
4. Consider CDN for static assets

## Future Enhancements

1. **Cache Warming**: Pre-populate cache on startup
2. **Distributed Cache**: Redis cluster for high availability
3. **Cache Metrics**: Prometheus/Grafana dashboards
4. **Smart Invalidation**: Event-driven cache invalidation
5. **Progressive Caching**: Cache partial results for long-running queries
