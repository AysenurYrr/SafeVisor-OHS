# ISG API ↔ ISG Web Integration Guide

## 🔗 How to Connect ISG API Backend with ISG Web Frontend

This guide explains how to set up and run both the ISG API (FastAPI backend) and ISG Web (React frontend) together.

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8+** (NOT Python 2.7) - for ISG API
- **Node.js 16+** (for ISG Web)
- **PostgreSQL** (or Docker for database)
- **Git** (for version control)

### ⚠️ Important: Python Version Requirements

**The ISG API requires Python 3.8 or higher.** If you see errors like:
```
Python 2.7.18
No module named venv
```

This means your system has Python 2.7 as the default `python` command, but you need Python 3.

#### Installing Python 3 on Windows:

**Option 1: Microsoft Store (Recommended for Windows 10/11)**
1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Install the official Python release
4. This will add `python3` command to your system

**Option 2: Official Python.org**
1. Visit https://python.org/downloads/
2. Download the latest Python 3.x installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Choose "Install for all users" if possible

**Option 3: Package Managers**
```cmd
# Chocolatey
choco install python

# Winget (Windows Package Manager)
winget install Python.Python.3.11
```

#### Verifying Python 3 Installation:
```cmd
# Try these commands to check:
python3 --version
py -3 --version
python --version
```

One of these should show "Python 3.x.x".

## 🚀 Quick Start (Recommended)

### Step 1: Start the Backend (ISG API)

1. **Open a terminal and navigate to the API directory:**
   ```cmd
   cd C:\Users\bilgisayar\Desktop\SafeVisor-OHS\isg-api
   ```

2. **Start the API server:**
   ```cmd
   # Quick start with automated setup (tries to detect Python 3)
   run.bat
   
   # OR use the Python 3 specific script
   run-python3.bat
   
   # OR start manually if you know your Python command
   # First activate virtual environment
   venv\Scripts\activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Verify the API is running:**
   - Open http://localhost:8000 in your browser
   - You should see: `{"message": "ISG Safety API", "version": "1.0.0", "docs": "/docs"}`
   - API Documentation: http://localhost:8000/docs

### Step 2: Start the Frontend (ISG Web)

1. **Open a NEW terminal and navigate to the web directory:**
   ```cmd
   cd C:\Users\bilgisayar\Desktop\SafeVisor-OHS\isg-web
   ```

2. **Install dependencies (first time only):**
   ```cmd
   npm install
   ```

3. **Start the development server:**
   ```cmd
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:5173
   - Login with: `admin@isg.com` / `admin123`

## 🐳 Using Docker (Alternative)

If you prefer to use Docker for the database:

1. **Start the database services:**
   ```cmd
   cd C:\Users\bilgisayar\Desktop\SafeVisor-OHS\isg-api
   docker-run.bat
   ```

2. **Run the API locally (connecting to Docker database):**
   ```cmd
   # Update .env file to use Docker database
   # DATABASE_URL=postgresql://isg:devpass@localhost:5432/isgdb
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start the frontend as usual:**
   ```cmd
   cd C:\Users\bilgisayar\Desktop\SafeVisor-OHS\isg-web
   npm run dev
   ```

## 🔧 Configuration Details

### Backend Configuration (ISG API)

The API is configured to accept requests from the frontend. Key configuration in `app/core/config.py`:

```python
# CORS Configuration
BACKEND_CORS_ORIGINS: list = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]
```

### Frontend Configuration (ISG Web)

The frontend is configured to connect to the backend via environment variables in `.env`:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## 🔐 Authentication Flow

1. **User logs in** through the frontend login form
2. **Frontend sends** credentials to `POST /auth/login`
3. **Backend validates** credentials and returns JWT tokens
4. **Frontend stores** tokens in localStorage
5. **All subsequent requests** include the Authorization header
6. **Token refresh** happens automatically when tokens expire

## 📊 API Endpoints Available

Once connected, the frontend can access:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Current user info
- `POST /auth/logout` - User logout

### Core Resources
- `GET /api/v1/employees/` - List employees
- `GET /api/v1/cameras/` - List cameras
- `GET /api/v1/violations/` - List PPE violations
- `GET /api/v1/pose-alerts/` - List pose alerts
- `GET /api/v1/users/` - List users (Admin only)

### Statistics & Reports
- `GET /api/v1/violations/stats/summary` - Violation statistics

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. **CORS Errors**
```
Error: Access to XMLHttpRequest blocked by CORS policy
```
**Solution:**
- Ensure the API is running on `http://localhost:8000`
- Check that `localhost:5173` is in the CORS origins list
- Restart the API server after making CORS changes

#### 2. **Network Connection Errors**
```
Error: Network Error or ERR_CONNECTION_REFUSED
```
**Solution:**
- Verify the API server is running: http://localhost:8000
- Check the frontend API base URL in `.env`
- Ensure no firewall is blocking the connection

#### 3. **Authentication Errors**
```
401 Unauthorized or Invalid credentials
```
**Solution:**
- Use the correct login credentials: `admin@isg.com` / `admin123`
- Ensure the database has the admin user (run the setup script)
- Check if the JWT secret key is configured correctly

#### 4. **Database Connection Issues**
```
Could not connect to database
```
**Solution:**
- Ensure PostgreSQL is running
- Check the DATABASE_URL in the `.env` file
- Run database migrations: `alembic upgrade head`
- For Docker: ensure containers are running: `docker compose ps`

#### 5. **Port Already in Use**
```
Error: Port 8000 is already in use
```
**Solution:**
- Kill the process using the port: `netstat -ano | findstr :8000`
- Use a different port: `uvicorn app.main:app --port 8001`
- Update the frontend API URL accordingly

#### 6. **Module Import Errors**
```
ModuleNotFoundError: No module named 'app'
```
**Solution:**
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Run from the correct directory (isg-api root)

#### 7. **Python 2.7 / venv Module Error**
```
Python 2.7.18
No module named venv
```
**Solution:**
- Install Python 3.8+ (see Prerequisites section above)
- Use `run-python3.bat` instead of `run.bat`
- Verify Python 3 installation: `python3 --version`
- On Windows, try: `py -3 --version`

### Environment-Specific Issues

#### Windows-Specific:
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- Use `run.bat` instead of `./run.sh`
- Check Windows Defender/Antivirus settings

#### Development vs Production:
- Development: Use `http://localhost:8000`
- Production: Update `VITE_API_BASE_URL` to your production API URL
- Ensure HTTPS in production
- Use environment-specific `.env` files

## 🔍 Testing the Connection

### 1. **Backend Health Check**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. **Login Test**
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@isg.com&password=admin123"
# Expected: JSON with access_token and refresh_token
```

### 3. **Frontend Connection Test**
1. Open browser to http://localhost:5173
2. Open Developer Tools (F12) → Network tab
3. Try to log in
4. Check for successful API calls to localhost:8000

## 📈 Monitoring & Debugging

### API Monitoring
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health endpoint:** http://localhost:8000/health

### Frontend Debugging
- **Console logs:** Check browser Developer Tools → Console
- **Network requests:** Developer Tools → Network tab
- **Local storage:** Developer Tools → Application → Local Storage

### Database Monitoring (with Docker)
- **pgAdmin:** http://localhost:5050
- **Login:** admin@isg.com / admin
- **Database:** Pre-configured ISG database connection

## 🚧 Development Workflow

### Typical Development Session:

1. **Start backend:**
   ```cmd
   cd isg-api
   run.bat
   ```

2. **Start frontend (new terminal):**
   ```cmd
   cd isg-web
   npm run dev
   ```

3. **Make changes:**
   - Backend changes auto-reload (with `--reload` flag)
   - Frontend changes auto-refresh (Vite HMR)

4. **Test changes:**
   - Use browser for frontend testing
   - Use http://localhost:8000/docs for API testing

## 📝 Environment Files Summary

### Backend (isg-api/.env)
```env
DATABASE_URL=postgresql://isg_user:isg_password@localhost/isg_db
SECRET_KEY=your-secret-key-here
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (isg-web/.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=ISG Safety Management
```

## 🆘 Getting Help

If you continue to experience issues:

1. **Check this guide** for common solutions
2. **Review the logs** in both terminals
3. **Test each service independently**
4. **Verify environment configuration**
5. **Check firewall/antivirus settings**

## 🎯 Success Criteria

You know the connection is working when:

✅ Backend API responds at http://localhost:8000  
✅ Frontend loads at http://localhost:5173  
✅ Login with admin@isg.com works  
✅ Navigation between pages works  
✅ Data loads in tables/components  
✅ No CORS errors in browser console  
✅ API calls visible in Network tab  

---

**Happy coding! 🚀**