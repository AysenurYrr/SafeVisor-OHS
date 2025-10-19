# Getting Started After Security Updates

## Default Credentials

After the security updates, the default admin credentials are:

```
Email: admin@isg.com
Password: admin123
```

**⚠️ IMPORTANT**: These are development credentials only. Change them before deploying to production!

## Other Demo Accounts

```
Manager:
Email: manager@isg.com
Password: manager123

HSE Expert:
Email: hse@isg.com
Password: hse123
```

## How to Start the Application

### Option 1: Docker (Recommended)

**Step 1**: Start the backend with Docker
```bash
cd isg-api
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

**Step 2**: Start the frontend
```bash
cd isg-web
npm install
npm run dev
```

**Step 3**: Access the application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development (Without Docker)

**Step 1**: Set up the backend

```bash
cd isg-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
cp .env.example .env

# Edit .env and set your database URL
# For SQLite (simplest): DATABASE_URL=sqlite:///./isg.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/isg_db

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 2**: Start the frontend
```bash
cd isg-web

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

**Step 3**: Access the application
- Frontend: http://localhost:5173
- Login with: admin@isg.com / admin123

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

This means dependencies aren't installed. Fix:

```bash
cd isg-api
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'slowapi'"

The security updates added a new dependency. Install it:

```bash
cd isg-api
pip install slowapi==0.1.9
# Or install all dependencies:
pip install -r requirements.txt
```

### Error: Import errors or "uvicorn/config.py" issues

Make sure you're in the right directory and have activated the virtual environment:

```bash
cd isg-api
# Activate venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Try running again
uvicorn app.main:app --reload
```

### Database Issues

If you get database errors:

**For SQLite** (easiest for development):
```bash
cd isg-api
# Edit .env file
DATABASE_URL=sqlite:///./isg.db

# Restart the application
```

**For PostgreSQL** (recommended for production):
```bash
# Make sure PostgreSQL is running
docker compose up -d db

# Update .env
DATABASE_URL=postgresql://isg:devpass@localhost:5432/isgdb

# Restart the application
```

### Can't Login / Authentication Issues

After the security updates, tokens are now stored in HttpOnly cookies instead of localStorage. This means:

1. **Clear your browser cache and cookies** for localhost
2. **Close all browser tabs** with the application
3. **Restart the application** (both frontend and backend)
4. **Try logging in again** with admin@isg.com / admin123

### CORS Errors

If you see CORS errors in the browser console:

1. Make sure backend is running on port 8000
2. Make sure frontend is running on port 5173
3. Check that `BACKEND_CORS_ORIGINS` in backend `.env` includes your frontend URL

### Port Already in Use

If you get "port already in use" errors:

**Backend (port 8000)**:
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process and restart
```

**Frontend (port 5173)**:
```bash
# Vite will automatically try the next available port (5174, 5175, etc.)
# Or kill the process using port 5173
```

## Quick Reference

### Checking if Services are Running

**Backend**:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

**Frontend**:
Open http://localhost:5173 in browser

**Database** (if using Docker):
```bash
docker ps | grep postgres
```

### Viewing Logs

**Backend (Docker)**:
```bash
docker compose logs -f api
```

**Backend (Local)**:
Check terminal where uvicorn is running

**Frontend**:
Check terminal where npm run dev is running

## What Changed in Security Updates

The recent security updates made these changes:

1. **Authentication**: Now uses HttpOnly cookies instead of localStorage
2. **Rate Limiting**: Added protection against brute-force attacks (5 attempts/minute)
3. **File Upload**: Added validation for image uploads
4. **Account Lockout**: Accounts lock for 15 minutes after 5 failed login attempts
5. **CORS**: Made configurable for production deployment

These changes are **backward compatible** - existing functionality still works, just more securely.

## Need Help?

1. Check `SECURITY_CONFIGURATION.md` for production deployment
2. Check `SECURITY_IMPLEMENTATION.md` for technical details
3. Check `Readme.md` for general information
4. Check API documentation at http://localhost:8000/docs

## Next Steps

Once you're logged in:

1. **Dashboard**: View safety metrics and alerts
2. **Employees**: Manage employee records
3. **Cameras**: View and manage cameras
4. **Factory Areas**: Manage factory areas and camera assignments
5. **Events**: View violations and pose alerts
6. **Admin > Users**: Manage user accounts (Admin only)
