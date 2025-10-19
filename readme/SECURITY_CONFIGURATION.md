# Production Security Configuration Guide

This guide covers the essential security configurations needed to deploy SafeVisor OHS to production.

## Table of Contents
1. [Backend Security Configuration](#backend-security-configuration)
2. [Frontend Security Configuration](#frontend-security-configuration)
3. [HTTPS Setup](#https-setup)
4. [Database Security](#database-security)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Security Checklist](#security-checklist)

## Backend Security Configuration

### 1. Environment Variables

Copy `.env.example` to `.env` and configure the following:

```bash
# Required Changes for Production
ENVIRONMENT=production
SECRET_KEY=<generate-a-strong-random-key-minimum-32-characters>
DATABASE_URL=<your-production-database-url>
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
USE_HTTPS=true
COOKIE_SECURE=true
COOKIE_DOMAIN=.yourdomain.com
FIRST_SUPERUSER_PASSWORD=<strong-unique-password>
```

#### Generating a Secure Secret Key

Use Python to generate a secure random key:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use OpenSSL:

```bash
openssl rand -base64 32
```

### 2. Cookie Security

The application uses HttpOnly cookies for JWT tokens, which provides protection against XSS attacks.

**Production settings:**
- `COOKIE_SECURE=true` - Cookies only sent over HTTPS
- `COOKIE_SAMESITE=lax` - CSRF protection (or `strict` for maximum security)
- `COOKIE_DOMAIN=.yourdomain.com` - Set to your domain

### 3. Rate Limiting

The application includes rate limiting for login attempts:
- `RATE_LIMIT_ENABLED=true` - Enable rate limiting
- `LOGIN_RATE_LIMIT=5/minute` - Limit login attempts per IP address

Adjust these based on your expected traffic patterns.

### 4. CORS Configuration

In production, restrict CORS to your actual frontend domain(s):

```bash
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

**Do NOT use wildcards (*) in production.**

### 5. File Upload Security

The application validates file uploads:
- File type validation (content-based, not just extension)
- File size limits (default 10MB)
- Filename sanitization to prevent path traversal
- Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`

Adjust `MAX_FILE_SIZE` and `ALLOWED_UPLOAD_EXTENSIONS` as needed.

### 6. Password Security

Passwords are hashed using Argon2, which is recommended by OWASP.

**Account Lockout:**
- After 5 failed login attempts, the account is locked for 15 minutes
- Generic error messages prevent user enumeration

### 7. Token Expiration

Configure token lifetimes based on your security requirements:
- `ACCESS_TOKEN_EXPIRE_MINUTES=30` - Short-lived access tokens
- `REFRESH_TOKEN_EXPIRE_DAYS=7` - Longer-lived refresh tokens

Shorter access token lifetimes are more secure but may impact user experience.

## Frontend Security Configuration

### 1. Environment Variables

Create `.env.production` with:

```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_DEV_MODE=false
```

### 2. Build Configuration

Ensure production builds are optimized:

```bash
npm run build
```

The built files will be in the `dist/` directory.

### 3. Content Security Policy (CSP)

Add CSP headers to your web server configuration. Example for Nginx:

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.yourdomain.com;" always;
```

### 4. Security Headers

Add these headers to your web server:

```nginx
# Nginx example
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

## HTTPS Setup

**HTTPS is required for production.** HttpOnly cookies with the `Secure` flag will only be sent over HTTPS.

### Option 1: Let's Encrypt (Free)

Use Certbot to obtain and automatically renew SSL certificates:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Option 2: Cloud Provider SSL

Most cloud providers (AWS, Azure, GCP) offer managed SSL certificates.

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Frontend
    location / {
        root /var/www/safevisor-frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Auth endpoints
    location /auth/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Database Security

### 1. Connection Security

- Use SSL/TLS for database connections in production
- Example: `postgresql://user:pass@host:5432/db?sslmode=require`

### 2. Credentials

- Never commit database credentials to version control
- Use strong, unique passwords
- Rotate credentials regularly
- Limit database user permissions (principle of least privilege)

### 3. Backups

- Set up automated daily backups
- Store backups securely and encrypted
- Test restore procedures regularly

### 4. Access Control

- Use a firewall to restrict database access
- Only allow connections from application servers
- Consider using a VPN for database access

## Monitoring and Logging

### 1. Application Logs

- Configure logging to capture security events
- Monitor failed login attempts
- Track API errors and unusual patterns
- Use log aggregation tools (ELK Stack, Splunk, etc.)

### 2. Security Monitoring

- Set up alerts for:
  - Multiple failed login attempts
  - Unusual API access patterns
  - File upload errors
  - Rate limit violations
- Consider using a security monitoring service (e.g., Datadog, New Relic)

### 3. Audit Logs

The application includes audit logging for:
- User logins/logouts
- User creation/modification
- Employee record changes
- Administrative actions

Review these logs regularly.

## Security Checklist

Before deploying to production, verify:

### Backend
- [ ] `SECRET_KEY` is unique and strong (minimum 32 characters)
- [ ] `ENVIRONMENT=production`
- [ ] `USE_HTTPS=true`
- [ ] `COOKIE_SECURE=true`
- [ ] `COOKIE_DOMAIN` is set to your domain
- [ ] `BACKEND_CORS_ORIGINS` restricted to frontend domain(s)
- [ ] Database uses SSL/TLS connection
- [ ] Strong database password configured
- [ ] `FIRST_SUPERUSER_PASSWORD` changed from default
- [ ] Rate limiting is enabled
- [ ] File upload limits are appropriate

### Frontend
- [ ] `VITE_API_BASE_URL` points to production API
- [ ] `VITE_DEV_MODE=false`
- [ ] Production build created (`npm run build`)
- [ ] Static files served over HTTPS
- [ ] CSP headers configured
- [ ] Security headers configured

### Infrastructure
- [ ] HTTPS/SSL certificate installed and valid
- [ ] Firewall configured (only necessary ports open)
- [ ] Database not publicly accessible
- [ ] Regular backups configured
- [ ] Monitoring and alerting configured
- [ ] Log aggregation configured

### Testing
- [ ] Login/logout tested in production-like environment
- [ ] Token expiration and refresh tested
- [ ] Role-based access control verified
- [ ] File upload validation tested
- [ ] HTTPS redirect working
- [ ] Cross-tab session behavior tested
- [ ] Rate limiting tested

## Additional Security Measures

### 1. Web Application Firewall (WAF)

Consider using a WAF service like:
- Cloudflare
- AWS WAF
- Azure WAF
- Imperva

### 2. DDoS Protection

Use DDoS protection services:
- Cloudflare
- AWS Shield
- Azure DDoS Protection

### 3. Vulnerability Scanning

Regularly scan for vulnerabilities:
- Use tools like OWASP ZAP or Burp Suite
- Enable GitHub Dependabot for dependency updates
- Run `npm audit` and `pip audit` regularly

### 4. Penetration Testing

Consider professional penetration testing before launch and periodically thereafter.

### 5. Security Updates

- Monitor security advisories for dependencies
- Apply security patches promptly
- Test updates in staging before production

## Support and Questions

For security concerns or questions:
1. Review the application documentation
2. Check for updates and security patches
3. Consult with security professionals for critical deployments

## Security Disclosure

If you discover a security vulnerability, please report it responsibly:
1. Do not publicly disclose the vulnerability
2. Contact the development team privately
3. Allow reasonable time for a fix before disclosure

## Operational Flexibility Flags (Advanced)

In rare cases you may need production to behave like development temporarily. The API exposes two feature flags, configurable via environment variables, to relax certain controls without redeploying code. Use them sparingly and monitor closely.

- RELAX_CAMERA_AUTH (default: false)
    - When true, camera streaming and detection endpoints skip auth/role checks, matching development behavior. Turn on only behind network protections (e.g., VPN) and disable ASAP after the incident.

- RELAX_REFRESH_DB_MISS (default: false)
    - When true, the refresh endpoint accepts a valid, unexpired refresh JWT even if its DB record is missing (useful after DB resets/token table purges). This preserves sessions while you reconcile token storage.

Example:

```
ENVIRONMENT=production
RELAX_CAMERA_AUTH=true
RELAX_REFRESH_DB_MISS=true
```

After enabling, restart the API service. Track usage via logs and plan to revert to secure defaults promptly.
