# SafeVisor-OHS

Monorepo containing:
- `isg-api` — FastAPI backend (JWT auth, RBAC, Alembic, Postgres/SQLite)
- `isg-web` — React + Vite frontend integrating with the backend

## Quickstart (Windows)

### Backend
```cmd
cd isg-api
run.bat
rem or
run-python3.bat
```

This creates a venv, installs deps, creates a default `.env` (SQLite by default), runs migrations (if available), seeds roles/admin, and starts the API at http://localhost:8000.

Default admin:
- Email: admin@isg.com
- Password: admin123

If needed, re-seed:
```cmd
cd isg-api
venv\Scripts\activate
python scripts\seed_admin.py
```

### Frontend
```cmd
cd isg-web
npm install
npm run dev
```

Ensure `isg-web/.env.development` contains:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Docker (DB + pgAdmin)
From `isg-api`:
```cmd
docker compose up -d
```
- Postgres: localhost:5432
- pgAdmin: http://localhost:5050

## Documentation
- See `isg-api/README.md` for API details
- See `isg-web/README.md` for frontend details
- **See `SECURITY_CONFIGURATION.md` for production security setup**

## Security Features

This application implements production-grade security measures:

### Authentication & Authorization
- **HttpOnly Cookies**: JWT tokens stored in HttpOnly cookies to prevent XSS attacks
- **Argon2 Password Hashing**: Industry-standard password hashing algorithm
- **Account Lockout**: Automatic lockout after failed login attempts (15 minutes)
- **Rate Limiting**: Protection against brute-force attacks (5 login attempts per minute)
- **Generic Error Messages**: Prevents user enumeration attacks

### Data Security
- **File Upload Validation**: Content-based file type checking and size limits
- **Filename Sanitization**: Prevention of path traversal attacks
- **Input Validation**: All user inputs are validated and sanitized
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

### Network Security
- **HTTPS Support**: Configured for HTTPS in production
- **CORS Restrictions**: Configurable CORS origins (no wildcards in production)
- **Secure Cookies**: SameSite and Secure flags for CSRF protection

### Access Control
- **Role-Based Access Control (RBAC)**: Admin, Manager, HSE Expert roles
- **Protected Routes**: Frontend and backend route protection
- **Audit Logging**: Comprehensive logging of user actions

### Production Deployment
Before deploying to production:
1. Review `SECURITY_CONFIGURATION.md` thoroughly
2. Update all environment variables (especially `SECRET_KEY`)
3. Enable HTTPS and set `COOKIE_SECURE=true`
4. Configure proper CORS origins
5. Set strong passwords for admin accounts
6. Enable monitoring and logging

⚠️ **Default credentials are for development only. Change them before deploying to production!**

docker exec -it isg-api alembic current

## Sıfırdan
1. terminal
- Docker başlatılmalıdır.
- cd isg-api
- docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

2. terminal 
- cd isg-web
- npm run dev

---

Sadece API kodunu değiştirdiğinde şu yeterli:

docker compose restart isg-api
npm run dev