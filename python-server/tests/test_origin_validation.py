"""
Tests for origin validation middleware
"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

# Set environment to development for testing
os.environ['ENVIRONMENT'] = 'development'

from app import app

client = TestClient(app)

def test_health_endpoint_no_origin_required():
    """Health check should work without origin header"""
    response = client.get("/health")
    assert response.status_code == 200

def test_docs_blocked_in_production():
    """Test that /docs is blocked in production"""
    with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
        # Need to recreate app with production setting
        from importlib import reload
        import app as app_module
        reload(app_module)
        test_app = app_module.app
        test_client = TestClient(test_app)
        
        response = test_client.get("/docs")
        assert response.status_code == 403

def test_docs_available_in_development():
    """Test that /docs is available in development"""
    with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
        response = client.get("/docs")
        # In development, docs should be available (200) or redirect to /docs (307)
        assert response.status_code in [200, 307]

def test_public_api_without_valid_origin():
    """Test that public API endpoints are blocked without valid origin"""
    response = client.get("/api/courses", headers={})
    assert response.status_code == 403
    assert "Access forbidden" in response.json().get("error", "")

def test_public_api_with_valid_origin():
    """Test that public API endpoints work with valid origin"""
    response = client.get(
        "/api/courses",
        headers={"Origin": "http://localhost:4200"}
    )
    # Should not be blocked by origin validation (might fail for other reasons like DB)
    # We're just checking it's not a 403 from origin validation
    assert response.status_code != 403 or "Access forbidden" not in response.json().get("error", "")

def test_public_api_with_valid_referer():
    """Test that public API endpoints work with valid referer"""
    response = client.get(
        "/api/courses",
        headers={"Referer": "http://localhost:4200/courses"}
    )
    # Should not be blocked by origin validation
    assert response.status_code != 403 or "Access forbidden" not in response.json().get("error", "")

def test_authenticated_api_bypasses_origin_check():
    """Test that authenticated requests bypass origin validation"""
    # Create a mock token (this won't be valid, but should bypass origin check)
    response = client.get(
        "/api/courses/my-courses",
        headers={"Authorization": "Bearer fake_token_for_testing"}
    )
    # Should not get 403 from origin validation (will get 401 from invalid token)
    assert response.status_code != 403 or "Access forbidden" not in response.json().get("error", "")

def test_public_api_with_invalid_origin():
    """Test that public API endpoints are blocked with invalid origin"""
    response = client.get(
        "/api/courses",
        headers={"Origin": "https://malicious-site.com"}
    )
    assert response.status_code == 403
    assert "Access forbidden" in response.json().get("error", "")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
