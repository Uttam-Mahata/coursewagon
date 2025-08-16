# FastAPI Authentication Middleware Migration Guide

This guide explains how to migrate from Flask-JWT-Extended to FastAPI with JWT authentication.

## Key Changes

### 1. Dependencies vs Decorators

**Flask (Old)**:
```python
from middleware.auth_middleware import require_auth
from flask_jwt_extended import get_jwt_identity

@app.route('/api/protected', methods=['GET'])
@require_auth
def protected_endpoint():
    user_id = get_jwt_identity()
    return jsonify({"user_id": user_id})
```

**FastAPI (New)**:
```python
from middleware.auth_middleware import get_current_user_id

@app.get("/api/protected")
async def protected_endpoint(current_user_id: int = Depends(get_current_user_id)):
    return {"user_id": current_user_id}
```

### 2. Library Changes

- **Flask-JWT-Extended** → **FastAPI-JWT-Auth**
- **Flask** → **FastAPI**
- **@app.route()** → **@app.get()/@app.post()/etc.**

### 3. Configuration Changes

**Flask config.py (Old)**:
```python
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_TOKEN_LOCATION = ['headers']
JWT_HEADER_NAME = 'Authorization'
JWT_HEADER_TYPE = 'Bearer'
```

**FastAPI Settings (New)**:
```python
from pydantic import BaseModel

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv('JWT_SECRET_KEY')
    authjwt_access_token_expires: timedelta = timedelta(hours=1)
    authjwt_token_location: set = {'headers'}
    authjwt_header_name: str = 'Authorization'
    authjwt_header_type: str = 'Bearer'

@AuthJWT.load_config
def get_config():
    return Settings()
```

## Migration Steps

### Step 1: Update requirements.txt

Ensure you have:
```
fastapi
fastapi-jwt-auth
uvicorn[standard]  # ASGI server for FastAPI
```

You can remove:
```
flask
flask-jwt-extended
gunicorn  # if you're switching to uvicorn
```

### Step 2: Update Authentication Middleware

The new auth middleware provides:
- `get_current_user_id()` - Main dependency for protected routes
- `get_current_user_optional()` - For optional authentication
- `require_auth()` - Backward compatibility decorator (not recommended)

### Step 3: Migrate Route Definitions

#### Flask Blueprint → FastAPI Router

**Flask**:
```python
from flask import Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    pass
```

**FastAPI**:
```python
from fastapi import APIRouter
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post("/login")
async def login():
    pass
```

#### Request/Response Handling

**Flask**:
```python
from flask import request, jsonify

@app.route('/api/user', methods=['POST'])
@require_auth
def create_user():
    data = request.get_json()
    user_id = get_jwt_identity()
    # ... logic ...
    return jsonify({"success": True})
```

**FastAPI**:
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/api/user")
async def create_user(
    user_data: UserCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    # ... logic ...
    return {"success": True}
```

### Step 4: Update Main Application

**Flask**:
```python
from flask import Flask
from flask_jwt_extended import JWTManager

app = Flask(__name__)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
```

**FastAPI**:
```python
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT

app = FastAPI()

# Include routers
app.include_router(auth_router)

# JWT configuration
@AuthJWT.load_config
def get_config():
    return Settings()
```

### Step 5: Update Error Handling

**Flask**:
```python
from flask import jsonify

try:
    # ... logic ...
except Exception as e:
    return jsonify({"error": str(e)}), 400
```

**FastAPI**:
```python
from fastapi import HTTPException

try:
    # ... logic ...
except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## Benefits of FastAPI Migration

1. **Better Performance**: ASGI vs WSGI
2. **Automatic Documentation**: OpenAPI/Swagger
3. **Type Safety**: Pydantic models with validation
4. **Async Support**: Native async/await support
5. **Better IDE Support**: Type hints for autocompletion
6. **Modern Python**: Built for Python 3.6+

## Testing the Migration

1. Start the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```

2. Test authentication endpoints:
   ```bash
   # Login to get token
   curl -X POST "http://localhost:8000/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "test", "password": "test"}'

   # Use token for protected route
   curl -X GET "http://localhost:8000/protected" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

3. Check automatic API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Common Issues and Solutions

### Issue 1: Token Validation Errors
- Ensure JWT secret key is consistent
- Check token expiration settings
- Verify Authorization header format

### Issue 2: CORS Issues
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: Database Integration
- Use `databases` library for async database operations
- Or use SQLAlchemy with async support
- Consider using FastAPI-SQLAlchemy for easier integration

## Next Steps

1. Test each endpoint individually
2. Update frontend to handle FastAPI response format
3. Set up proper logging configuration
4. Configure production deployment with uvicorn
5. Update CI/CD pipelines for FastAPI
