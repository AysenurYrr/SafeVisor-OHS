@echo off
setlocal enabledelayedexpansion
REM ISG API Startup Script for Windows

echo ========================================
echo     ISG Safety API Startup Script
echo ========================================
echo.

REM Check if Python 3 is installed and determine the correct command
set PYTHON_CMD=
set PYTHON_VERSION=

REM Try python3 first (preferred)
python3 --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [INFO] Found Python 3: !PYTHON_VERSION!
    set PYTHON_CMD=python3
    goto :python_found
)

REM Try py -3 (Python Launcher for Windows)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%i in ('py -3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [INFO] Found Python 3 via launcher: !PYTHON_VERSION!
    set PYTHON_CMD=py -3
    goto :python_found
)

REM Try python (but verify it's Python 3)
python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [INFO] Found Python: !PYTHON_VERSION!
    REM Check if it's Python 3
    echo !PYTHON_VERSION! | findstr /C:"3." >nul
    if not errorlevel 1 (
        set PYTHON_CMD=python
        goto :python_found
    ) else (
        echo [WARNING] Found Python !PYTHON_VERSION! but need Python 3.8+
    )
)

REM If we get here, no suitable Python was found
echo ERROR: Python 3.8+ is not installed or not in PATH!
echo.
echo Please install Python 3.8+ from https://python.org
echo Make sure to:
echo 1. Check "Add Python to PATH" during installation
echo 2. Install for all users (if possible)
echo 3. Restart your command prompt after installation
echo.
echo Alternative installation methods:
echo - Microsoft Store: "python3"
echo - Chocolatey: "choco install python"
echo - Direct download: https://python.org/downloads/
echo.
pause
exit /b 1

:python_found
echo [SUCCESS] Using Python command: %PYTHON_CMD%

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo [INFO] Virtual environment already exists.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Install/upgrade requirements
echo [INFO] Installing dependencies...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    echo Please check requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed.

REM Set environment variables (if .env file doesn't exist)
if not exist ".env" (
    echo [INFO] Creating .env file with default settings...
    (
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///./isg.db
        echo.
        echo # Security Settings
        echo SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo REFRESH_TOKEN_EXPIRE_DAYS=7
        echo.
        echo # CORS Settings
        echo BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
        echo.
        echo # Default Admin User
        echo FIRST_SUPERUSER_EMAIL=admin@isg.com
        echo FIRST_SUPERUSER_PASSWORD=admin123
        echo.
        echo # Application Info
        echo PROJECT_NAME=ISG Safety API
        echo VERSION=1.0.0
        echo DESCRIPTION=Occupational Safety Management System API
    ) > .env
    echo [SUCCESS] .env file created with SQLite configuration.
    echo [WARNING] Using SQLite for development. For production, configure PostgreSQL!
) else (
    echo [INFO] .env file already exists.
)

REM Check if Alembic is initialized
if not exist "alembic\versions" (
    echo [INFO] Initializing database migrations...
    alembic revision --autogenerate -m "Initial migration" --quiet
    if errorlevel 1 (
        echo [WARNING] Failed to create initial migration. This might be normal for first run.
    )
)

REM Run database migrations
echo [INFO] Running database migrations...
alembic upgrade head --quiet
if errorlevel 1 (
    echo [WARNING] Migration failed. Database might need manual setup.
    echo [INFO] Continuing with startup...
)

REM Create initial data
echo [INFO] Setting up initial data...
%PYTHON_CMD% -c "
try:
    from app.db.session import SessionLocal
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    
    # Create roles
    roles = [
        {'name': 'Admin', 'description': 'System Administrator', 'is_active': True},
        {'name': 'Manager', 'description': 'Department Manager', 'is_active': True},
        {'name': 'AssistantManager', 'description': 'Assistant Manager', 'is_active': True},
        {'name': 'HSEExpert', 'description': 'Health Safety Environment Expert', 'is_active': True}
    ]
    
    for role_data in roles:
        role = db.query(Role).filter(Role.name == role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    
    # Create admin user
    admin_role = db.query(Role).filter(Role.name == 'Admin').first()
    admin = db.query(User).filter(User.email == 'admin@isg.com').first()
    if not admin and admin_role:
        admin = User(
            email='admin@isg.com',
            username='admin',
            full_name='System Administrator',
            hashed_password=get_password_hash('admin123'),
            is_active=True,
            is_superuser=True,
            role_id=admin_role.id
        )
        db.add(admin)
        db.commit()
        print('[SUCCESS] Admin user created.')
    else:
        print('[INFO] Admin user already exists.')
    
    db.close()
except Exception as e:
    print(f'[WARNING] Initial data setup failed: {e}')
    print('[INFO] You can create admin user manually later.')
" 2>nul

echo.
echo ========================================
echo          Starting FastAPI Server
echo ========================================
echo [INFO] Server starting at: http://localhost:8000
echo [INFO] API Documentation: http://localhost:8000/docs
echo [INFO] Admin Login: admin@isg.com / admin123
echo.
echo [INFO] Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [INFO] Server stopped.
pause