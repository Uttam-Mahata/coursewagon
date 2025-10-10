# Caching Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CourseWagon Application                          │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐       ┌──────────────────────────────┐
│      Angular Frontend        │       │      Python Backend          │
│                              │       │                              │
│  ┌────────────────────────┐  │       │  ┌────────────────────────┐  │
│  │  Cache Interceptor     │  │       │  │   Cache Helper         │  │
│  │  (HTTP GET caching)    │  │       │  │   (Redis/Memory)       │  │
│  │  TTL: 3 minutes        │  │       │  │   TTL: 3-10 minutes    │  │
│  └────────────────────────┘  │       │  └────────────────────────┘  │
│            ↕                 │       │            ↕                 │
│  ┌────────────────────────┐  │       │  ┌────────────────────────┐  │
│  │   Cache Service        │  │       │  │   Service Layer        │  │
│  │   - Memory Cache       │  │       │  │   - Course Service     │  │
│  │   - LocalStorage       │  │       │  │   - Subject Service    │  │
│  │   - Pattern Invalidate │  │       │  │   - Topic Service      │  │
│  └────────────────────────┘  │       │  │   - Content Service    │  │
│            ↕                 │       │  └────────────────────────┘  │
│  ┌────────────────────────┐  │       │            ↕                 │
│  │   HTTP Services        │  │ ====► │  ┌────────────────────────┐  │
│  │   - CourseService      │  │       │  │   Repository Layer     │  │
│  │   - SubjectService     │  │       │  │   - Optimized Queries  │  │
│  │   - TopicService       │  │       │  │   - Eager Loading      │  │
│  │   - ContentService     │  │       │  └────────────────────────┘  │
│  └────────────────────────┘  │       │            ↕                 │
└──────────────────────────────┘       │  ┌────────────────────────┐  │
                                       │  │   MySQL Database       │  │
                                       │  │   - Connection Pool    │  │
                                       │  │   - 15+ Indexes        │  │
                                       │  └────────────────────────┘  │
                                       └──────────────────────────────┘
```

## Request Flow with Caching

### First Request (Cache Miss)

```
User Request
    ↓
Angular Component
    ↓
HTTP Service
    ↓
Cache Interceptor → [Check Cache] → MISS
    ↓
API Request
    ↓
Backend Route
    ↓
Service Layer → [Check Cache Helper] → MISS
    ↓
Repository Layer
    ↓
Database Query (with indexes)
    ↓
Result
    ↓
Service Layer → [Store in Cache]
    ↓
Backend Response
    ↓
Cache Interceptor → [Store in HTTP Cache]
    ↓
HTTP Service → [Store in Memory/LocalStorage]
    ↓
Angular Component → Display to User
```

### Subsequent Request (Cache Hit)

```
User Request
    ↓
Angular Component
    ↓
HTTP Service
    ↓
Cache Interceptor → [Check Cache] → HIT! → Return Cached Response
    ↓
Angular Component → Display to User (Instant!)
```

### Backend Cache Hit

```
API Request
    ↓
Backend Route
    ↓
Service Layer → [Check Cache Helper] → HIT! → Return Cached Data
    ↓
Backend Response (Instant - no DB query!)
```

## Cache Layers

```
┌────────────────────────────────────────────────────────────┐
│                    Frontend Caching                        │
├────────────────────────────────────────────────────────────┤
│ Layer 1: HTTP Interceptor Cache                            │
│   - Automatic GET request caching                          │
│   - TTL: 3 minutes                                         │
│   - Transparent to services                                │
├────────────────────────────────────────────────────────────┤
│ Layer 2: Memory Cache (CacheService)                       │
│   - Fast in-memory storage                                 │
│   - TTL: Configurable per key                              │
│   - Pattern-based invalidation                             │
├────────────────────────────────────────────────────────────┤
│ Layer 3: LocalStorage Cache                                │
│   - Persistent across sessions                             │
│   - TTL: Configurable (minutes)                            │
│   - Automatic quota management                             │
├────────────────────────────────────────────────────────────┤
│ Layer 4: Observable Cache (shareReplay)                    │
│   - Request deduplication                                  │
│   - Prevents duplicate in-flight requests                  │
│   - Shares results with multiple subscribers               │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                    Backend Caching                         │
├────────────────────────────────────────────────────────────┤
│ Layer 1: Redis Cache (Primary)                             │
│   - Fast, distributed caching                              │
│   - TTL: 3-10 minutes based on data type                   │
│   - Shared across application instances                    │
├────────────────────────────────────────────────────────────┤
│ Layer 2: In-Memory Cache (Fallback)                        │
│   - Used when Redis unavailable                            │
│   - TTL: Same as Redis                                     │
│   - Per-instance (not shared)                              │
└────────────────────────────────────────────────────────────┘
```

## Cache Key Hierarchy

```
Backend Cache Keys:
├── courses
│   ├── courses:all (all courses list)
│   ├── courses:user:{user_id} (user's courses)
│   └── course:{id} (individual course)
├── subjects
│   ├── subjects:course:{course_id} (subjects for course)
│   └── subject:{id} (individual subject)
├── topics
│   ├── topics:chapter:{chapter_id} (topics for chapter)
│   └── topic:{id} (individual topic)
├── content
│   └── content:topic:{topic_id} (content for topic)
└── users
    ├── user:{id} (user profile)
    └── user:{id}:* (user-related data)

Frontend Cache Keys:
├── http
│   └── http:{urlWithParams} (HTTP response cache)
├── courses
│   ├── courses: (course lists)
│   └── course:{id} (individual course)
└── user
    └── user:{id}:* (user-specific data)
```

## Cache Invalidation Flow

```
User Updates Course
    ↓
Frontend → HTTP PUT/POST/DELETE
    ↓
Backend Service
    ↓
Database Update
    ↓
Cache Invalidation:
    ├── invalidate_cache(f"course:{course_id}")
    ├── invalidate_cache(f"courses:user:{user_id}")
    ├── invalidate_cache("courses:all")
    └── invalidate_cache(f"subjects:course:{course_id}")
    ↓
Response to Frontend
    ↓
Frontend Invalidation:
    ├── cacheService.delete(f"course:{courseId}")
    ├── cacheService.invalidate("courses:")
    └── HTTP cache automatically invalidated (non-GET)
    ↓
Next Request → Cache Miss → Fresh Data
```

## Performance Metrics

```
┌─────────────────────────────────────────────────────────┐
│              Before Optimization                        │
├─────────────────────────────────────────────────────────┤
│ Average Response Time:  200-500ms                       │
│ Database Queries:       High load                       │
│ Duplicate Requests:     Frequent                        │
│ User Experience:        Loading spinners everywhere     │
└─────────────────────────────────────────────────────────┘

                          ↓  Optimization

┌─────────────────────────────────────────────────────────┐
│              After Optimization                         │
├─────────────────────────────────────────────────────────┤
│ Cached Response Time:   <10ms (95% faster)             │
│ Database Queries:       70-90% reduction               │
│ Duplicate Requests:     Eliminated                      │
│ User Experience:        Instant responses               │
└─────────────────────────────────────────────────────────┘
```

## TTL Strategy

```
Data Type           | TTL     | Reason
--------------------|---------|--------------------------------
Courses (list)      | 5 min   | Moderate change frequency
User courses        | 3 min   | User-specific, changes often
Subjects/Topics     | 5 min   | Structure changes infrequently
Content             | 10 min  | Expensive to generate
HTTP responses      | 3 min   | Balance freshness vs performance
User profile        | 5 min   | Rarely changes
Static config       | 30 min  | Very stable
```

## Database Indexes

```
Indexed Columns (15+):
├── course
│   ├── user_id (FK)
│   ├── is_published
│   ├── category
│   └── published_at
├── subject
│   └── course_id (FK)
├── chapter
│   └── subject_id (FK)
├── topic
│   ├── subject_id (FK)
│   └── chapter_id (FK)
├── content
│   └── topic_id (FK)
├── user
│   ├── email
│   └── firebase_uid
├── enrollment
│   ├── user_id (FK)
│   ├── course_id (FK)
│   └── status
└── learning_progress
    ├── user_id (FK)
    └── content_id (FK)

Performance Impact:
├── SELECT queries: 50-90% faster
├── JOIN operations: 70-85% faster
├── WHERE clauses: 60-80% faster
└── ORDER BY: 40-60% faster
```

## Monitoring Points

```
┌─────────────────────────────────────────────────────────┐
│                  Cache Monitoring                       │
├─────────────────────────────────────────────────────────┤
│ Frontend:                                               │
│   - Console logs: [Cache] Hit/Miss                     │
│   - Cache stats: cacheService.getCacheStats()          │
│                                                         │
│ Backend:                                                │
│   - Logger: "Cache hit/miss for {key}"                 │
│   - Redis status: cache_helper.use_redis               │
│   - Memory cache fallback tracking                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Database Monitoring                        │
├─────────────────────────────────────────────────────────┤
│ Connection Pool:                                        │
│   - Pool size: 20 connections                           │
│   - Max overflow: 30 additional                         │
│   - Pool timeout: 30 seconds                            │
│                                                         │
│ Query Performance:                                      │
│   - Explain analyze on slow queries                     │
│   - Index usage tracking                                │
│   - Query execution time logs                           │
└─────────────────────────────────────────────────────────┘
```

## Scalability

```
Single Instance:
┌──────────────┐
│  App Server  │
│  ┌────────┐  │     ┌─────────┐
│  │ Memory │  │ ──► │  MySQL  │
│  │ Cache  │  │     │  (Pool) │
│  └────────┘  │     └─────────┘
└──────────────┘

Multiple Instances with Redis:
┌──────────────┐     ┌──────────────┐
│ App Server 1 │     │ App Server 2 │
│  ┌────────┐  │     │  ┌────────┐  │
│  │ Memory │  │     │  │ Memory │  │
│  │ Cache  │  │     │  │ Cache  │  │
│  └────────┘  │     │  └────────┘  │
└──────┬───────┘     └──────┬───────┘
       │                    │
       └──────────┬─────────┘
                  ↓
          ┌──────────────┐
          │    Redis     │  ← Shared cache
          │   Cluster    │
          └──────┬───────┘
                 ↓
          ┌──────────────┐
          │    MySQL     │
          │  (Replicas)  │
          └──────────────┘
```

---

**Legend:**
- ↕ : Bidirectional communication
- ↓ : Data flow direction
- ====► : HTTP/API communication
- ─── : Connection/Relationship
