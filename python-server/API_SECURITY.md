# API Access Restriction and Documentation Security

## Overview

This implementation adds security measures to restrict API access and hide documentation endpoints in production. The solution ensures that:

1. **API endpoints** are only accessible from authorized frontend domains
2. **Documentation endpoints** (`/docs`, `/redoc`) are disabled in production
3. **OpenAPI schema** (`/openapi.json`) is not publicly accessible in production

## Changes Made

### 1. Origin Validation Middleware

**File:** `python-server/middleware/origin_validation_middleware.py`

A new middleware that validates the `Origin` and `Referer` headers for incoming requests:

- **Public API endpoints** (unauthenticated): Must include valid Origin/Referer header matching allowed domains
- **Authenticated endpoints**: Bypass origin check (protected by JWT authentication)
- **Documentation endpoints**: Blocked in production environment
- **Health check**: Always accessible without restrictions

### 2. FastAPI Application Updates

**File:** `python-server/app.py`

Modified the FastAPI application initialization to:

- Conditionally disable docs/redoc/openapi endpoints based on `ENVIRONMENT` variable
- Add the `OriginValidationMiddleware` to the middleware stack
- Import and configure the new middleware with allowed origins

```python
# Disable docs in production
IS_PRODUCTION_ENV = os.environ.get('ENVIRONMENT', 'development') == 'production'
app = FastAPI(
    docs_url=None if IS_PRODUCTION_ENV else "/docs",
    redoc_url=None if IS_PRODUCTION_ENV else "/redoc",
    openapi_url=None if IS_PRODUCTION_ENV else "/openapi.json"
)

# Add origin validation middleware
app.add_middleware(OriginValidationMiddleware, allowed_origins=allowed_origins)
```

### 3. Deployment Configuration

**File:** `.github/workflows/deploy.yml`

Updated Cloud Run deployment to set the `ENVIRONMENT=production` variable:

```yaml
--set-env-vars="FIREBASE_ADMIN_SDK_PATH=/etc/secrets/firebase/admin-sdk.json,ENVIRONMENT=production"
```

### 4. Tests

**File:** `python-server/tests/test_origin_validation.py`

Comprehensive test suite covering:

- Documentation endpoint blocking in production
- Documentation endpoint availability in development
- Public API access with valid/invalid origins
- Authenticated request handling
- Various origin/referer header scenarios

## How It Works

### Request Flow

```
Request → Origin Validation Middleware → CORS Middleware → Route Handler
```

1. **Request arrives** at the server
2. **Origin Validation Middleware** checks:
   - Is it a health check? → Allow
   - Is it OPTIONS (CORS preflight)? → Allow
   - Is it /docs, /redoc, /openapi.json in production? → Block (403)
   - Is it an authenticated API request? → Allow (auth middleware will validate)
   - Is it a public API request?
     - Has valid Origin/Referer? → Allow
     - No valid Origin/Referer? → Block (403)
3. **CORS Middleware** handles cross-origin policy
4. **Route handler** processes the request

### Allowed Origins

The following origins are allowed in production:

- `https://coursewagon.live`
- `https://www.coursewagon.live`
- `https://coursewagon.web.app`
- `https://coursewagon.alphaaiservice.com`

In development, localhost is also allowed:

- `http://localhost:4200`
- `http://127.0.0.1:4200`

## Security Model

### Public Endpoints (No Authentication)

Examples: `GET /api/courses`, `GET /api/courses/120001/subjects`

**Requirements:**
- Must include `Origin` or `Referer` header
- Origin must match one of the allowed domains
- Requests from browsers automatically include these headers
- Direct curl/API calls without proper headers will be blocked

### Authenticated Endpoints

Examples: `GET /api/courses/my-courses`, `POST /api/courses/add_course`

**Requirements:**
- Must include valid JWT token (in cookie or Authorization header)
- Origin validation is bypassed (authentication is sufficient)
- Protected by existing JWT authentication middleware

### Documentation Endpoints

Examples: `/docs`, `/redoc`, `/openapi.json`

**Production:** Completely disabled (returns 404)
**Development:** Accessible for testing and debugging

### Health Check

Example: `/health`

**Always accessible** - no restrictions for monitoring purposes

## Testing

### Running Tests

```bash
cd python-server
python -m pytest tests/test_origin_validation.py -v
```

### Manual Testing

#### Test 1: Docs in Production

```bash
# Should return 403 or 404 (blocked)
curl -I https://api.coursewagon.live/docs
```

#### Test 2: Public API without Origin

```bash
# Should return 403 (blocked)
curl https://api.coursewagon.live/api/courses
```

#### Test 3: Public API with Valid Origin

```bash
# Should return course data (allowed)
curl -H "Origin: https://www.coursewagon.live" https://api.coursewagon.live/api/courses
```

#### Test 4: Authenticated API

```bash
# Should return 401 (unauthorized) not 403 (origin blocked)
curl -H "Authorization: Bearer invalid_token" https://api.coursewagon.live/api/courses/my-courses
```

## Environment Variables

### Required for Production

- `ENVIRONMENT=production` - Enables production security features

### Behavior by Environment

| Environment | Docs Endpoints | Origin Validation | Allowed Origins |
|-------------|----------------|-------------------|-----------------|
| production  | Disabled       | Enabled           | Production domains only |
| development | Enabled        | Enabled           | Production domains + localhost |

## Browser Behavior

Modern browsers automatically include `Origin` or `Referer` headers:

- **Same-origin requests**: Include Origin header
- **Cross-origin requests**: Include Origin header
- **Navigation**: Include Referer header
- **Fetch/XHR**: Include Origin header

This means legitimate frontend applications will automatically pass validation, while direct API access (curl, Postman without proper headers) will be blocked.

## Limitations and Considerations

### Origin/Referer Header Spoofing

While Origin/Referer headers can theoretically be manipulated in custom HTTP clients, modern browsers enforce these headers securely:

- Browsers prevent JavaScript from modifying Origin header
- Browsers enforce CORS policies
- Combined with CORS, this provides strong protection against browser-based attacks

### Authenticated Endpoints

Authenticated endpoints rely on JWT authentication rather than origin validation, as the presence of a valid JWT token is a stronger security guarantee.

### Rate Limiting

The existing rate limiting middleware continues to protect against abuse even if origin validation is bypassed.

### Mobile Apps and Native Clients

If you plan to support mobile apps or native clients:

1. They should authenticate and use authenticated endpoints
2. Or, you'll need to add additional authentication mechanisms (API keys, etc.)
3. Origin validation primarily protects against unauthorized web-based access

## Troubleshooting

### Issue: Frontend can't access API

**Check:**
1. Is the frontend origin in the allowed_origins list?
2. Is ENVIRONMENT variable set correctly?
3. Check browser console for CORS errors

### Issue: Authenticated requests blocked

**Check:**
1. Is the JWT token present in cookies or Authorization header?
2. Is the token valid and not expired?
3. Check server logs for authentication errors

### Issue: Tests failing

**Check:**
1. Is ENVIRONMENT set to 'development' for tests?
2. Are test dependencies installed? (httpx, pytest)
3. Is the database accessible for integration tests?

## Deployment Checklist

- [ ] Ensure `ENVIRONMENT=production` is set in Cloud Run
- [ ] Verify allowed_origins includes all production frontend domains
- [ ] Test that /docs returns 403 or 404 in production
- [ ] Test that frontend can still access API
- [ ] Monitor logs for unexpected 403 errors
- [ ] Verify authenticated endpoints still work

## Future Enhancements

1. **API Key Authentication**: Add support for API keys for programmatic access
2. **Request Signing**: Implement HMAC request signing for additional security
3. **Advanced Rate Limiting**: Per-origin rate limiting
4. **Monitoring**: Add metrics for blocked requests
5. **Whitelisting**: IP-based whitelisting for trusted clients

## References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [CORS (Cross-Origin Resource Sharing)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Origin Header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Origin)
- [Referer Header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referer)
