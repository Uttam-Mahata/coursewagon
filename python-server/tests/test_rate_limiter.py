"""
Tests for rate limiting functionality
"""
import pytest
import time
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from utils.rate_limiter import (
    limiter,
    get_auth_rate_limit,
    get_ai_rate_limit,
    get_utility_rate_limit,
    get_admin_rate_limit,
    get_content_rate_limit,
    get_public_rate_limit,
    AUTH_RATE_LIMITS,
    AI_RATE_LIMITS,
    UTILITY_RATE_LIMITS,
    ADMIN_RATE_LIMITS,
    CONTENT_RATE_LIMITS,
    PUBLIC_RATE_LIMITS,
    DEFAULT_RATE_LIMIT
)


def test_rate_limit_configurations():
    """Test that rate limit configurations are properly defined"""
    # Check auth limits exist
    assert "check_email" in AUTH_RATE_LIMITS
    assert "login" in AUTH_RATE_LIMITS
    assert "register" in AUTH_RATE_LIMITS
    assert "forgot_password" in AUTH_RATE_LIMITS
    
    # Check AI limits exist
    assert "generate_image" in AI_RATE_LIMITS
    assert "generate_course_image" in AI_RATE_LIMITS
    
    # Check utility limits exist
    assert "proxy_image" in UTILITY_RATE_LIMITS
    assert "check_image" in UTILITY_RATE_LIMITS
    
    # Check admin limits exist
    assert "dashboard" in ADMIN_RATE_LIMITS
    assert "user_management" in ADMIN_RATE_LIMITS
    
    # Check content limits exist
    assert "create_course" in CONTENT_RATE_LIMITS
    assert "update_content" in CONTENT_RATE_LIMITS
    
    # Check public limits exist
    assert "get_courses" in PUBLIC_RATE_LIMITS
    assert "get_content" in PUBLIC_RATE_LIMITS


def test_get_auth_rate_limit():
    """Test getting auth rate limits"""
    # Test known endpoint
    assert get_auth_rate_limit("check_email") == "10/minute"
    assert get_auth_rate_limit("login") == "10/minute"
    assert get_auth_rate_limit("register") == "5/hour"
    
    # Test unknown endpoint returns default
    assert get_auth_rate_limit("unknown_endpoint") == DEFAULT_RATE_LIMIT


def test_get_ai_rate_limit():
    """Test getting AI rate limits"""
    # Test known endpoint
    assert get_ai_rate_limit("generate_image") == "10/hour"
    assert get_ai_rate_limit("generate_course_image") == "20/hour"
    
    # Test unknown endpoint returns default
    assert get_ai_rate_limit("unknown_endpoint") == DEFAULT_RATE_LIMIT


def test_get_utility_rate_limit():
    """Test getting utility rate limits"""
    # Test known endpoint
    assert get_utility_rate_limit("proxy_image") == "60/minute"
    assert get_utility_rate_limit("check_image") == "30/minute"
    
    # Test unknown endpoint returns default
    assert get_utility_rate_limit("unknown_endpoint") == DEFAULT_RATE_LIMIT


def test_get_admin_rate_limit():
    """Test getting admin rate limits"""
    # Test known endpoint
    assert get_admin_rate_limit("dashboard") == "60/minute"
    assert get_admin_rate_limit("user_management") == "30/minute"
    
    # Test unknown endpoint returns default
    assert get_admin_rate_limit("unknown_endpoint") == DEFAULT_RATE_LIMIT


def test_get_content_rate_limit():
    """Test getting content rate limits"""
    # Test known endpoint
    assert get_content_rate_limit("create_course") == "20/hour"
    assert get_content_rate_limit("update_content") == "100/hour"
    
    # Test unknown endpoint returns default
    assert get_content_rate_limit("unknown_endpoint") == DEFAULT_RATE_LIMIT


def test_get_public_rate_limit():
    """Test getting public rate limits"""
    # Test known endpoint
    assert get_public_rate_limit("get_courses") == "100/minute"
    assert get_public_rate_limit("get_content") == "200/minute"
    
    # Test unknown endpoint returns default
    assert get_public_rate_limit("unknown_endpoint") == DEFAULT_RATE_LIMIT


def test_limiter_initialization():
    """Test that limiter is properly initialized"""
    assert limiter is not None
    # Check that limiter has default limits configured
    assert len(limiter._default_limits) > 0
    assert limiter._headers_enabled is True
    assert limiter._swallow_errors is True


def test_rate_limit_format():
    """Test that all rate limit strings follow the correct format"""
    all_limits = {
        **AUTH_RATE_LIMITS,
        **AI_RATE_LIMITS,
        **UTILITY_RATE_LIMITS,
        **ADMIN_RATE_LIMITS,
        **CONTENT_RATE_LIMITS,
        **PUBLIC_RATE_LIMITS
    }
    
    valid_periods = ["second", "minute", "hour", "day"]
    
    for endpoint, limit in all_limits.items():
        # Format should be "count/period"
        parts = limit.split("/")
        assert len(parts) == 2, f"Invalid format for {endpoint}: {limit}"
        
        count, period = parts
        assert count.isdigit(), f"Count should be numeric for {endpoint}: {count}"
        assert period in valid_periods, f"Invalid period for {endpoint}: {period}"


def test_auth_limits_are_strict():
    """Test that auth endpoints have stricter limits than public endpoints"""
    # Check email should be limited to prevent enumeration
    check_email_limit = int(AUTH_RATE_LIMITS["check_email"].split("/")[0])
    assert check_email_limit <= 10, "check_email should have strict limit"
    
    # Register should be limited to prevent abuse
    register_limit_str = AUTH_RATE_LIMITS["register"]
    assert "hour" in register_limit_str, "register should be limited per hour"
    
    # Login should be limited to prevent brute force
    login_limit = int(AUTH_RATE_LIMITS["login"].split("/")[0])
    assert login_limit <= 10, "login should have strict limit"
    
    # Forgot password should be very strict
    forgot_password_limit = int(AUTH_RATE_LIMITS["forgot_password"].split("/")[0])
    assert forgot_password_limit <= 5, "forgot_password should have very strict limit"


def test_ai_limits_are_strict():
    """Test that AI endpoints have strict limits due to compute cost"""
    # All AI limits should be per hour (expensive operations)
    for endpoint, limit in AI_RATE_LIMITS.items():
        assert "hour" in limit, f"AI endpoint {endpoint} should be limited per hour"
        
        count = int(limit.split("/")[0])
        assert count <= 30, f"AI endpoint {endpoint} should have strict hourly limit"


def test_public_limits_are_generous():
    """Test that public read endpoints have generous limits"""
    # Public endpoints should allow more requests
    get_courses_limit = int(PUBLIC_RATE_LIMITS["get_courses"].split("/")[0])
    assert get_courses_limit >= 50, "get_courses should have generous limit"
    
    get_content_limit = int(PUBLIC_RATE_LIMITS["get_content"].split("/")[0])
    assert get_content_limit >= 100, "get_content should have generous limit"


def test_rate_limiter_with_test_app():
    """Test rate limiter integration with a test FastAPI app"""
    from fastapi.responses import JSONResponse
    from slowapi.errors import RateLimitExceeded
    
    # Create a test app
    app = FastAPI()
    app.state.limiter = limiter
    
    # Add exception handler for rate limiting
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    @app.get("/test")
    @limiter.limit("5/minute")
    async def test_endpoint(request: Request):
        return JSONResponse(content={"message": "success"})
    
    client = TestClient(app)
    
    # First 5 requests should succeed
    for i in range(5):
        response = client.get("/test")
        assert response.status_code == 200
    
    # 6th request should be rate limited
    response = client.get("/test")
    assert response.status_code == 429
    
    # Check rate limit headers are present or status is 429
    assert response.status_code == 429


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
