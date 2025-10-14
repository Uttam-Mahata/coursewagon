# Rate Limiting Documentation

## Overview

The CourseWagon API implements comprehensive rate limiting to protect against abuse, prevent resource exhaustion, and ensure fair usage across all users. Rate limiting is implemented using [SlowAPI](https://slowapi.readthedocs.io/), a FastAPI extension that provides flexible and Redis-backed rate limiting.

## Architecture

### Components

1. **Rate Limiter Module** (`utils/rate_limiter.py`)
   - Central configuration for all rate limits
   - Categorized limits for different endpoint types
   - Redis backend with in-memory fallback
   - Custom key function for per-user vs per-IP limiting

2. **FastAPI Integration** (`app.py`)
   - Rate limiter state attached to app
   - Custom error handler for rate limit exceeded errors
   - Returns standard 429 status codes with retry information

3. **Route Decorators**
   - `@limiter.limit()` decorators applied to specific endpoints
   - Category-specific limit functions (e.g., `get_auth_rate_limit()`)

## Rate Limit Categories

### Authentication Endpoints (`AUTH_RATE_LIMITS`)

Strict limits to prevent abuse and enumeration attacks:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `check_email` | 10/minute | Email enumeration protection |
| `validate_email` | 10/minute | Email validation checks |
| `register` | 5/hour | User registration |
| `login` | 10/minute | Login attempts (brute force protection) |
| `forgot_password` | 3/hour | Password reset requests |
| `reset_password` | 5/hour | Password reset submissions |
| `refresh_token` | 30/minute | Token refresh |
| `verify_email` | 10/hour | Email verification |
| `resend_verification` | 3/hour | Resend verification email |

**Security Notes:**
- Low limits prevent credential stuffing and brute force attacks
- Email enumeration limited to prevent discovery of registered users
- Password reset limits prevent abuse of email system

### AI/Image Generation Endpoints (`AI_RATE_LIMITS`)

Strict limits due to compute cost and API quotas:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `generate_image` | 10/hour | AI image generation |
| `generate_course_image` | 20/hour | Course-specific image generation |
| `generate_subject_image` | 30/hour | Subject image generation |

**Cost Considerations:**
- AI operations are expensive (Gemini API calls)
- Hourly limits prevent quota exhaustion
- Per-user tracking ensures fair usage

### Utility/Proxy Endpoints (`UTILITY_RATE_LIMITS`)

Moderate limits for proxy and utility services:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `proxy_image` | 60/minute | Image proxy service |
| `check_image` | 30/minute | Image availability check |
| `direct_image` | 20/hour | Direct image generation |

### Admin Endpoints (`ADMIN_RATE_LIMITS`)

Moderate limits for admin operations:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `dashboard` | 60/minute | Admin dashboard access |
| `user_management` | 30/minute | User management operations |

### Content Creation Endpoints (`CONTENT_RATE_LIMITS`)

Reasonable limits for content creators:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `create_course` | 20/hour | Course creation |
| `update_content` | 100/hour | Content updates |
| `delete_content` | 50/hour | Content deletion |

### Public/Read Endpoints (`PUBLIC_RATE_LIMITS`)

Generous limits for content browsing:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `get_courses` | 100/minute | Browse courses |
| `get_content` | 200/minute | View content |
| `search` | 50/minute | Search functionality |

## Configuration

### Storage Backend

The rate limiter supports two storage backends:

#### Redis (Production - Recommended)

```bash
# Environment variables
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-password  # Optional
```

**Benefits:**
- Distributed rate limiting across multiple server instances
- Persistent rate limit counters
- Scalable for production workloads

#### In-Memory (Development Fallback)

If Redis is not configured, the limiter automatically falls back to in-memory storage.

**Limitations:**
- Rate limits reset when server restarts
- Not suitable for multi-instance deployments
- Only for development/testing

### Rate Limit Key Strategy

The limiter uses different keys based on authentication status:

```python
def get_rate_limit_key(request: Request) -> str:
    """
    - Authenticated: Rate limit by user_id (more accurate)
    - Unauthenticated: Rate limit by IP address
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    else:
        return get_remote_address(request)
```

**Advantages:**
- Authenticated users are limited per account (not shared by IP)
- Multiple users behind same IP don't share rate limits
- Prevents VPN/proxy circumvention for authenticated endpoints

## Response Format

### Successful Request

Standard API response with rate limit headers:

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1234567890
```

### Rate Limit Exceeded

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

## Testing

### Unit Tests

Run the comprehensive rate limiter test suite:

```bash
cd python-server
python -m pytest tests/test_rate_limiter.py -v
```

Tests cover:
- Configuration validation
- Limit retrieval functions
- Format validation
- Security policy checks
- Integration with FastAPI

### Manual Testing

Test rate limiting with curl:

```bash
# Test auth endpoint (10/minute limit)
for i in {1..12}; do
  curl -X POST http://localhost:8000/api/auth/check-email \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com"}' \
    -w "\nStatus: %{http_code}\n" \
    -s | grep -E "(Status|error)"
done
```

Expected:
- First 10 requests: Status 200
- 11th+ requests: Status 429

## Monitoring

### Rate Limit Headers

All responses include rate limit information:

- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when the limit resets

### Logging

Rate limit events are logged at INFO level:

```python
# When initialized
INFO: Rate limiter using Redis storage at redis-host:6379

# Or fallback
WARNING: Rate limiter using in-memory storage. Use Redis for production.
```

### Redis Monitoring

Monitor Redis keys for rate limiting:

```bash
# List all rate limit keys
redis-cli KEYS "LIMITER:*"

# Check specific user's limits
redis-cli KEYS "LIMITER:user:123:*"

# View key TTL (time to expiration)
redis-cli TTL "LIMITER:user:123:/api/auth/login"
```

## Customization

### Adding New Limits

To add rate limiting to a new endpoint:

1. **Add to configuration** (`utils/rate_limiter.py`):

```python
AUTH_RATE_LIMITS = {
    # ... existing limits ...
    "new_endpoint": "15/minute",
}
```

2. **Apply decorator** to route:

```python
from utils.rate_limiter import limiter, get_auth_rate_limit

@router.post('/new-endpoint')
@limiter.limit(get_auth_rate_limit("new_endpoint"))
async def new_endpoint(request: Request, ...):
    pass
```

### Adjusting Existing Limits

Modify limits in `utils/rate_limiter.py`:

```python
AUTH_RATE_LIMITS = {
    "login": "15/minute",  # Changed from 10/minute
}
```

**Note:** Restart the application for changes to take effect.

### Environment-Specific Limits

Use environment variables for dynamic limits:

```python
import os

AUTH_RATE_LIMITS = {
    "login": os.getenv("LOGIN_RATE_LIMIT", "10/minute"),
}
```

## Best Practices

### For Developers

1. **Choose appropriate categories**: Use existing rate limit categories when possible
2. **Test with limits**: Run tests to ensure limits don't break normal usage
3. **Document changes**: Update this document when adding new endpoints
4. **Consider user impact**: Balance security with user experience

### For Operations

1. **Use Redis in production**: In-memory storage is not production-ready
2. **Monitor rate limit hits**: Track 429 errors to identify potential issues
3. **Adjust limits based on usage**: Review and adjust limits as needed
4. **Set up alerting**: Alert on excessive 429 errors (may indicate attack or misconfiguration)

### For Security

1. **Review logs regularly**: Check for patterns of rate limit abuse
2. **Implement IP blocking**: Consider blocking IPs that consistently hit rate limits
3. **Monitor authentication endpoints**: Pay special attention to login and registration limits
4. **Coordinate with WAF/CDN**: Ensure rate limiting complements other security layers

## Troubleshooting

### Issue: Rate limits not working

**Possible causes:**
- Limiter not attached to app state
- Missing `request: Request` parameter in endpoint
- Rate limiter decorator not applied

**Solution:**
- Verify `app.state.limiter = limiter` in `app.py`
- Ensure endpoint has `request: Request` parameter
- Check that `@limiter.limit()` decorator is applied

### Issue: All requests return 429

**Possible causes:**
- Redis connection issues
- Extremely low rate limits
- Time synchronization problems

**Solution:**
- Check Redis connectivity: `redis-cli ping`
- Review rate limit configuration
- Verify server time is correct

### Issue: Rate limits not shared across instances

**Possible causes:**
- Using in-memory storage instead of Redis
- Different Redis instances for each server

**Solution:**
- Configure Redis properly with `REDIS_HOST`
- Ensure all instances use the same Redis server

## Security Considerations

### Rate Limit Bypass Attempts

**Attack vectors:**
- IP rotation (VPN/proxy)
- Distributed attacks
- Cookie/token manipulation

**Mitigations:**
- Per-user rate limiting for authenticated endpoints
- Additional IP-based rate limiting at CDN/WAF level
- Anomaly detection for suspicious patterns

### Denial of Service

**Concern:** Attackers hitting rate limits to cause 429 errors

**Mitigations:**
- Rate limits are per-user/IP (attacks don't affect other users)
- Automatic blocking of repeat offenders (future enhancement)
- CDN-level rate limiting as first line of defense

### Information Disclosure

**Concern:** Rate limit headers reveal endpoint behavior

**Current approach:** Headers enabled for better developer experience

**Alternative:** Disable headers in production:
```python
limiter = Limiter(
    headers_enabled=False  # Hide rate limit info
)
```

## Future Enhancements

1. **Dynamic rate limiting**: Adjust limits based on user tier or subscription
2. **Bypass whitelist**: Allow certain trusted IPs to bypass limits
3. **Burst allowance**: Allow short bursts above the limit
4. **Rate limit analytics**: Dashboard showing rate limit usage patterns
5. **Auto-ban**: Automatically block IPs that consistently abuse limits
6. **Per-endpoint Redis keys**: Better tracking and clearing of specific endpoint limits

## References

- [SlowAPI Documentation](https://slowapi.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [OWASP Rate Limiting Guide](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html#rate-limiting)
