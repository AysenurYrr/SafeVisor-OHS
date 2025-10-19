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

**Wait for the build to complete.** This may take a few minutes the first time as it installs all dependencies including the new `slowapi` package.

**Step 2**: Verify containers are running
```bash
docker ps
```

You should see containers named `isg-api`, `isgdb`, and `isg-pgadmin` with status "Up".

**Step 3**: Check the API is healthy
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

If containers aren't running, check logs:
```bash
docker compose logs api
docker compose logs db
```

**Step 4**: Start the frontend
```bash
cd isg-web
npm install
npm run dev
```

**Step 5**: Access the application
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

### Docker Issues

#### Containers not starting or "nothing happened"

If you ran `docker compose up` but the containers aren't running:

```bash
cd isg-api

# Check if containers are running
docker ps

# Check all containers (including stopped)
docker ps -a

# View logs to see what went wrong
docker compose logs

# View specific service logs
docker compose logs api
docker compose logs db

# If build failed, rebuild from scratch
docker compose down -v
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

#### Docker build failing with dependency errors

The Docker build automatically installs all dependencies including `slowapi`. If the build fails:

```bash
cd isg-api

# Clean everything and rebuild
docker compose down -v
docker system prune -f
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Watch the logs in real-time
docker compose logs -f api
```

#### Container exits immediately

Check logs to see why:

```bash
docker compose logs api
```

Common causes:
- Database not ready (wait 30 seconds and check again)
- Port 8000 already in use (stop other services using that port)
- Import errors (rebuild with `--no-cache`)

#### Port conflicts

If port 8000 or 5432 is already in use:

```bash
# Find what's using the port (Linux/Mac)
lsof -i :8000
lsof -i :5432

# Find what's using the port (Windows)
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Stop the conflicting process or change ports in docker-compose.dev.yml
```

### Local Development (Non-Docker) Issues

#### Error: "ModuleNotFoundError: No module named 'fastapi'"

This means dependencies aren't installed. Fix:

```bash
cd isg-api
pip install -r requirements.txt
```

#### Error: "ModuleNotFoundError: No module named 'slowapi'"

The security updates added a new dependency. Install it:

```bash
cd isg-api
pip install slowapi==0.1.9
# Or install all dependencies:
pip install -r requirements.txt
```

#### Error: Import errors or "uvicorn/config.py" issues

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

## Common Issue: "I ran docker compose but nothing happened"

If you ran the Docker command but don't see any containers running or can't access the application:

### Step 1: Check if containers are actually running

```bash
cd isg-api
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE          COMMAND                  STATUS         PORTS                    NAMES
abc123...      isg-api        "uvicorn app.main:ap…"   Up 2 minutes   0.0.0.0:8000->8000/tcp   isg-api
def456...      postgres:16    "docker-entrypoint.s…"   Up 2 minutes   0.0.0.0:5432->5432/tcp   isgdb
ghi789...      pgadmin4       "/entrypoint.sh"         Up 2 minutes   0.0.0.0:5050->80/tcp     isg-pgadmin
```

**If you see nothing**, the containers failed to start. Check logs:

```bash
# View all logs
docker compose logs

# View just the API logs
docker compose logs api

# Follow logs in real-time
docker compose logs -f api
```

### Step 2: Common problems and solutions

**Problem: Import error for 'slowapi'**
```
ModuleNotFoundError: No module named 'slowapi'
```

**Solution:** The Docker image needs to be rebuilt to include the new dependency:
```bash
cd isg-api
docker compose down
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Problem: Database not ready**
```
could not connect to server: Connection refused
```

**Solution:** Wait 30 seconds for PostgreSQL to initialize, then restart the API:
```bash
docker compose restart api
```

**Problem: Port already in use**
```
bind: address already in use
```

**Solution:** Another service is using port 8000 or 5432. Either stop that service or change ports in docker-compose.dev.yml.

### Step 3: Verify the API is working

```bash
# Health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs  # Mac
# or visit http://localhost:8000/docs in browser
```

### Step 4: If still not working, do a complete reset

```bash
cd isg-api

# Stop everything
docker compose down -v

# Remove old images
docker rmi isg-api-api 2>/dev/null || true

# Rebuild from scratch
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache

# Start with logs visible
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Watch for errors in the output
# Once you see "Application startup complete", press Ctrl+C
# Then start in detached mode
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
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
