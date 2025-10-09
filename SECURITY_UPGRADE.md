# Security Upgrade: HttpOnly Cookie Authentication

## 🎉 What Was Implemented

Your CourseWagon application has been upgraded with **enterprise-grade security** for JWT authentication using **HttpOnly cookies** instead of localStorage.

### ✅ Completed Features

1. **Email Verification System**
   - Users must verify email before full account access
   - Verification emails sent via Gmail SMTP
   - Token-based email verification (24-hour expiry)
   - Resend verification functionality
   - Welcome email sent after verification

2. **Secure JWT Authentication**
   - HttpOnly cookies (immune to XSS attacks)
   - Automatic token refresh mechanism
   - Remember Me functionality
   - Secure logout with cookie clearing

3. **Email Validation**
   - DNS MX record checking
   - Disposable email blocking
   - Domain validation

---

## 🔒 Security Improvements

### Before (localStorage)
```typescript
// ❌ VULNERABLE to XSS
localStorage.setItem('auth_token', token);
// JavaScript can access and steal tokens
```

### After (HttpOnly Cookies)
```typescript
// ✅ SECURE - JavaScript cannot access
response.set_cookie(
    key="access_token",
    httponly=True,  // Cannot be accessed by JavaScript
    secure=True,    // HTTPS only
    samesite="lax"  // CSRF protection
)
```

---

## 📋 Setup Instructions

### 1. Run Database Migrations

```bash
cd python-server
python migrations/add_email_verification.py
```

This will:
- Add `email_verified` and `email_verification_sent_at` columns to user table
- Create `email_verification` table
- Mark existing users as verified

### 2. Environment Variables

Ensure these are set in `python-server/.env`:

```bash
# Email Configuration (Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Gmail App Password, not your regular password
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_CONTACT_EMAIL=support@coursewagon.live

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here  # IMPORTANT: Use a strong secret key

# Frontend URL
FRONTEND_URL=http://localhost:4200  # Or your production URL

# Environment
ENVIRONMENT=development  # Set to 'production' in prod
```

### 3. Start Services

**Backend:**
```bash
cd python-server
uvicorn app:app --reload
```

**Frontend:**
```bash
cd angular-client
npm start
```

---

## 🔄 How It Works

### Authentication Flow

1. **User Registers**
   ```
   POST /api/auth/register
   ↓
   Email validation (DNS MX check)
   ↓
   User created with email_verified=false
   ↓
   Verification email sent
   ↓
   User clicks email link
   ↓
   POST /api/auth/verify-email?token=xxx
   ↓
   email_verified=true
   ↓
   Welcome email sent
   ```

2. **User Logs In**
   ```
   POST /api/auth/login (withCredentials: true)
   ↓
   Backend sets HttpOnly cookies:
     - access_token (1 hour)
     - refresh_token (7 days)
   ↓
   Frontend stores user data in localStorage
   ↓
   All API requests automatically include cookies
   ```

3. **Token Refresh**
   ```
   API request returns 401
   ↓
   Interceptor calls POST /api/auth/refresh
   ↓
   New access_token cookie set
   ↓
   Original request retried
   ```

4. **User Logs Out**
   ```
   POST /api/auth/logout
   ↓
   Cookies cleared on backend
   ↓
   User data cleared from localStorage
   ↓
   Redirect to /auth
   ```

---

## 🛡️ Security Features

### 1. HttpOnly Cookies
- ✅ **Cannot be accessed by JavaScript** (immune to XSS)
- ✅ **Browser automatically includes in requests**
- ✅ **Secure flag** (HTTPS only in production)
- ✅ **SameSite protection** (CSRF prevention)

### 2. Token Expiry
- **Access Token**: 1 hour (30 days with Remember Me)
- **Refresh Token**: 7 days (30 days with Remember Me)
- Automatic refresh on expiry

### 3. CORS Configuration
- Exact origin matching (no wildcard with credentials)
- Credentials allowed
- Proper headers configuration

### 4. Email Verification
- Prevents fake account creation
- 24-hour token expiry
- One-time use tokens
- DNS validation

---

## 📝 API Changes

### Login Response (Before)
```json
{
  "access_token": "eyJ...",  // ❌ Exposed
  "refresh_token": "eyJ...", // ❌ Exposed
  "user": {...}
}
```

### Login Response (After)
```json
{
  "user": {...},  // ✅ Only user data
  "message": "Login successful"
}
// Tokens in HttpOnly cookies (not in response)
```

### New Endpoints
- `POST /api/auth/logout` - Clear cookies
- `POST /api/auth/verify-email` - Verify email
- `POST /api/auth/resend-verification` - Resend verification
- `GET /api/auth/verification-status` - Check verification
- `POST /api/auth/validate-email` - Validate email deliverability

---

## 🧪 Testing

### 1. Registration & Email Verification
```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","first_name":"Test","last_name":"User"}'

# Check your email for verification link
# Click link or use token:
curl -X POST http://localhost:8000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token":"your-token-here"}'
```

### 2. Login with Cookies
```bash
# Login (cookies set automatically)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","remember_me":false}' \
  --cookie-jar cookies.txt

# Access protected route
curl -X GET http://localhost:8000/api/auth/profile \
  --cookie cookies.txt
```

### 3. Token Refresh
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  --cookie cookies.txt
```

---

## 🚨 Important Notes

### For Development
- Cookies work on `localhost` without HTTPS
- Set `ENVIRONMENT=development` in `.env`
- CORS allows `http://localhost:4200`

### For Production
- **MUST use HTTPS** (secure flag enabled)
- Set `ENVIRONMENT=production` in `.env`
- Update `FRONTEND_URL` to production domain
- Add production domain to CORS `allow_origins`
- Use strong `JWT_SECRET_KEY`

### Gmail Setup
To send emails, you need a **Gmail App Password**:
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password for "Mail"
4. Use this password in `MAIL_PASSWORD`

---

## 🐛 Troubleshooting

### Issue: Cookies not being set
**Solution**: Check CORS configuration
```python
# Ensure these are set in app.py
allow_origins=[
    "http://localhost:4200",  # Must be exact match
],
allow_credentials=True,
```

### Issue: 401 errors on protected routes
**Solution**: Check if cookies are being sent
- Frontend must use `withCredentials: true`
- Interceptor automatically adds this

### Issue: Email verification not working
**Solution**: Check email service configuration
```bash
# Test email service
python -c "from services.email_service import EmailService; EmailService().test_smtp_connection()"
```

### Issue: Migration errors
**Solution**: Run migrations manually
```bash
python migrations/add_email_verification.py
```

---

## 📊 Database Schema

### User Table (Updated)
```sql
ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN email_verification_sent_at DATETIME NULL;
```

### Email Verification Table (New)
```sql
CREATE TABLE email_verification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

---

## 🎯 Benefits

| Feature | Before | After |
|---------|--------|-------|
| **XSS Protection** | ❌ Vulnerable | ✅ Immune |
| **Token Storage** | localStorage | HttpOnly Cookies |
| **Token Refresh** | ❌ Not implemented | ✅ Automatic |
| **Remember Me** | ⚠️ 30-day access token | ✅ Secure cookies |
| **Email Verification** | ❌ No verification | ✅ Required |
| **CSRF Protection** | ❌ None | ✅ SameSite cookies |
| **Security Score** | 🔴 Low | 🟢 High |

---

## 📚 References

- [OWASP JWT Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [HttpOnly Cookies](https://owasp.org/www-community/HttpOnly)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

## 🎉 You're All Set!

Your application now has **enterprise-grade security** with:
- ✅ HttpOnly cookie authentication
- ✅ Email verification
- ✅ Automatic token refresh
- ✅ CSRF protection
- ✅ XSS immunity

**Next Steps:**
1. Run the database migration
2. Test registration & login flow
3. Verify email functionality
4. Test Remember Me feature
5. Deploy to production with HTTPS

---

**Questions?** Check the code comments or refer to this documentation.
