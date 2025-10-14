# Security Policy

## Reporting a Vulnerability

The CourseWagon team takes security issues seriously. We appreciate your efforts to responsibly disclose your findings and will make every effort to acknowledge your contributions.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **Email**: Send details to the project maintainers (contact information in repository)
2. **GitHub Security Advisory**: Use the "Security" tab in this repository to privately report a vulnerability
3. **Encrypted Communication**: If the issue is highly sensitive, request a PGP key for encrypted communication

### What to Include

To help us understand and address the issue quickly, please include:

* **Type of issue** (e.g., SQL injection, XSS, authentication bypass, data exposure)
* **Full paths of source file(s)** related to the issue
* **Location of the affected source code** (tag/branch/commit or direct URL)
* **Step-by-step instructions** to reproduce the issue
* **Proof-of-concept or exploit code** (if possible)
* **Impact of the issue**, including how an attacker might exploit it
* **Any potential mitigations** you've identified

### Response Timeline

* **Initial Response**: Within 48 hours of receipt
* **Status Update**: Within 7 days with preliminary assessment
* **Resolution Timeline**: Varies by severity, but critical issues will be prioritized
* **Disclosure**: We follow coordinated disclosure practices

### What to Expect

1. **Acknowledgment**: We'll confirm receipt of your report
2. **Communication**: We'll keep you informed of progress
3. **Credit**: With your permission, we'll acknowledge your contribution in security advisories
4. **Fix Timeline**: We'll work to address verified vulnerabilities promptly
5. **Public Disclosure**: After a fix is deployed, we may publish a security advisory

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

**Recommendation**: Always use the latest version to ensure you have all security patches.

## Security Best Practices

### For Contributors

#### Code Security

1. **Input Validation**
   * Always validate and sanitize user input
   * Use parameterized queries to prevent SQL injection
   * Validate file uploads (type, size, content)
   * Implement rate limiting on API endpoints

2. **Authentication & Authorization**
   * Never hardcode credentials or API keys
   * Use environment variables for sensitive configuration
   * Implement proper JWT token validation
   * Verify user permissions before allowing actions
   * Use Firebase Admin SDK for token verification

3. **Data Protection**
   * Encrypt sensitive data at rest
   * Use HTTPS for all communications
   * Don't log sensitive information (passwords, tokens, PII)
   * Implement proper CORS policies
   * Hash passwords using bcrypt or similar

4. **Dependencies**
   * Regularly update dependencies to patch vulnerabilities
   * Run `npm audit` (frontend) and `pip audit` (backend) regularly
   * Review dependencies before adding them
   * Use lock files (package-lock.json, requirements.txt)

5. **API Security**
   * Implement authentication on all protected endpoints
   * Use appropriate HTTP methods and status codes
   * Validate request payloads against schemas
   * Implement request size limits
   * Add rate limiting to prevent abuse

#### Frontend Security (Angular)

```typescript
// Good: Use Angular's built-in XSS protection
<div [innerHTML]="sanitizedContent"></div>

// Bad: Bypassing security
<div [innerHTML]="unsafeContent | bypassSecurityTrust"></div>

// Good: Validate user input
if (!this.validateEmail(email)) {
  return;
}

// Good: Don't expose sensitive data in localStorage
// Use secure, httpOnly cookies when possible
```

#### Backend Security (FastAPI)

```python
# Good: Use parameterized queries
result = db.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})

# Bad: String concatenation
result = db.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Good: Verify JWT tokens
@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    pass

# Good: Validate input with Pydantic models
class UserInput(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
```

### For Deployers

#### Environment Configuration

1. **Never commit sensitive data to version control**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   *.key
   *.pem
   *-adminsdk*.json
   ```

2. **Use strong secrets**
   ```bash
   # Generate secure JWT secret
   openssl rand -hex 32
   
   # Use environment-specific secrets
   # Never reuse secrets across environments
   ```

3. **Required Environment Variables**
   ```bash
   # Backend (.env)
   DATABASE_URL=mysql+pymysql://user:pass@host/db
   JWT_SECRET_KEY=<strong-secret-key>
   JWT_REFRESH_SECRET_KEY=<strong-secret-key>
   FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json
   AZURE_STORAGE_CONNECTION_STRING=<connection-string>
   MAIL_USERNAME=<email>
   MAIL_PASSWORD=<app-password>
   GEMINI_API_KEY=<api-key>
   
   # Frontend (environment.ts)
   # Never commit API keys to repository
   ```

#### Database Security

1. **Use least privilege principle**
   * Create dedicated database users with minimal required permissions
   * Don't use root/admin accounts for application access
   * Regularly rotate database credentials

2. **Enable encryption**
   * Use SSL/TLS for database connections
   * Enable encryption at rest for sensitive data
   * Regular backups with encryption

3. **Connection pooling**
   * Properly configure connection pools to prevent exhaustion
   * Set reasonable timeouts
   * Monitor for connection leaks

#### Cloud Deployment

1. **Firebase Security**
   * Restrict API keys to specific domains
   * Enable App Check for additional protection
   * Configure Firebase Security Rules properly
   * Regular audit of Firebase users and permissions

2. **Azure/Cloud Storage**
   * Use SAS tokens with expiration for temporary access
   * Enable CORS only for trusted origins
   * Implement access policies and lifecycle management
   * Enable storage encryption

3. **API Deployment**
   * Enable WAF (Web Application Firewall) if available
   * Use HTTPS/TLS 1.2+ only
   * Application-level rate limiting implemented (SlowAPI with Redis)
   * Infrastructure-level rate limiting recommended (CDN/WAF)
   * Enable DDoS protection
   * Regular security scanning and penetration testing

#### Monitoring & Logging

1. **Log security events**
   * Failed authentication attempts
   * Authorization failures
   * Unusual API usage patterns
   * File upload attempts
   * Database errors

2. **Don't log sensitive data**
   * Passwords or password hashes
   * JWT tokens or session IDs
   * Credit card or payment information
   * Personal identification numbers
   * API keys or secrets

3. **Implement alerting**
   * Multiple failed login attempts
   * Unusual API access patterns
   * Database connection failures
   * High error rates

## Known Security Considerations

### Current Architecture

1. **Authentication Flow**
   * Firebase Auth for user authentication
   * JWT tokens for API authorization
   * Token refresh mechanism implemented
   * Tokens expire after 1 hour (configurable)

2. **Data Storage**
   * User passwords not stored (Firebase handles auth)
   * Sensitive data encrypted in database
   * File uploads stored in Azure/Firebase with access controls

3. **API Security**
   * CORS configured for specific origins
   * Comprehensive rate limiting implemented throughout the API (see `python-server/docs/RATE_LIMITING.md`)
   * Rate limits vary by endpoint category (auth, AI, content, public)
   * Redis-backed distributed rate limiting in production
   * Input validation using Pydantic models
   * SQL injection prevention via SQLAlchemy ORM

4. **AI Integration**
   * Gemini API key stored securely in environment
   * User input sanitized before AI processing
   * AI responses validated before storage

### Areas Under Active Development

* Enhanced audit logging system
* Two-factor authentication (2FA)
* Advanced rate limiting per user
* Content Security Policy (CSP) headers
* Security headers implementation (HSTS, X-Frame-Options)

## Security Checklist for Pull Requests

Before submitting code, ensure:

- [ ] No hardcoded secrets, passwords, or API keys
- [ ] All user input is validated and sanitized
- [ ] Authentication is required for protected endpoints
- [ ] Authorization checks verify user permissions
- [ ] SQL queries use parameterization or ORM
- [ ] File uploads are validated (type, size, content)
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies are up to date
- [ ] No console.log with sensitive data in production code
- [ ] CORS is properly configured
- [ ] Rate limiting is considered for new endpoints
- [ ] Tests include security-relevant scenarios

## Security Tools & Resources

### Automated Scanning

```bash
# Backend dependency scanning
pip install pip-audit
pip-audit

# Frontend dependency scanning
npm audit
npm audit fix

# Security linting
bandit -r python-server/
```

### Recommended Tools

* **OWASP ZAP**: Web application security scanner
* **Snyk**: Dependency vulnerability scanning
* **GitHub Dependabot**: Automated dependency updates
* **GitGuardian**: Secret detection in repositories
* **SonarQube**: Code quality and security analysis

### Resources

* [OWASP Top 10](https://owasp.org/www-project-top-ten/)
* [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
* [Angular Security Guide](https://angular.io/guide/security)
* [Firebase Security Best Practices](https://firebase.google.com/docs/rules/security)
* [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

## Compliance & Privacy

### Data Protection

* User data is processed in accordance with privacy regulations
* Personal information is encrypted and access-controlled
* Users can request data deletion (GDPR, CCPA compliance)
* Data retention policies are documented

### Educational Content

* AI-generated content is reviewed for accuracy
* User-generated content is moderated
* Copyright and intellectual property respected
* Academic integrity guidelines followed

## Security Updates

We publish security advisories for:

* **Critical**: Immediate action required (0-day, RCE, data breach)
* **High**: Significant vulnerabilities requiring prompt patching
* **Medium**: Security improvements in regular updates
* **Low**: Minor issues or hardening recommendations

Subscribe to repository notifications to stay informed about security updates.

## Questions?

If you have questions about this security policy or need clarification on security practices, please:

* Open a discussion in the repository (for general questions)
* Contact maintainers directly (for specific concerns)
* Review existing security documentation in the repository

---

**Last Updated**: January 2025

*This security policy is subject to updates as the project evolves. Please check back regularly for the latest information.*
