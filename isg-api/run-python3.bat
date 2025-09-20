@echo off
setlocal enabledelayedexpansion

echo =======================================
echo    ISG API Quick Start (Python 3)
echo =======================================
echo.

REM Simple Python 3 detection
set PYTHON_CMD=

REM Check common Python 3 commands
echo [INFO] Searching for Python 3...

REM Try python3 first
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    echo [SUCCESS] Found python3
    goto :start_setup
)

REM Try py launcher with -3 flag
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    echo [SUCCESS] Found Python 3 via py launcher
    goto :start_setup
)

REM Check if regular python is Python 3
python --version 2>&1 | findstr "Python 3" >nul
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo [SUCCESS] Found Python 3 as 'python'
    goto :start_setup
)

REM No Python 3 found
echo [ERROR] Python 3 not found!
echo.
echo Please install Python 3.8+ from one of these sources:
echo.
echo 1. Microsoft Store (Recommended for Windows 10/11):
echo    - Search for "Python 3.11" in Microsoft Store
echo    - Install and it will be available as 'python3'
echo.
echo 2. Official Python.org:
echo    - Visit https://python.org/downloads/
echo    - Download Python 3.8+ installer
echo    - Make sure to check "Add Python to PATH"
echo.
echo 3. Command line (if you have package managers):
echo    - Chocolatey: choco install python
echo    - Scoop: scoop install python
echo.
echo After installation, restart this command prompt and try again.
echo.
pause
exit /b 1

:start_setup
%PYTHON_CMD% --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo This usually means:
        echo 1. Python installation is incomplete
        echo 2. Missing python3-venv package (on Linux)
        echo 3. Insufficient permissions
        echo.
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
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Upgrade pip and install requirements
echo [INFO] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    echo Please check:
    echo 1. Internet connection
    echo 2. requirements.txt file exists
    echo 3. No firewall blocking pip
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies installed successfully!
echo.

REM Create .env file if needed
if not exist ".env" (
    echo [INFO] Creating .env configuration...
    (
        echo DATABASE_URL=sqlite:///./isg.db
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo REFRESH_TOKEN_EXPIRE_DAYS=7
        echo BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
        echo FIRST_SUPERUSER_EMAIL=admin@isg.com
        echo FIRST_SUPERUSER_PASSWORD=admin123
    ) > .env
    echo [SUCCESS] .env file created.
)

REM Run migrations
echo [INFO] Setting up database...
alembic upgrade head 2>nul
if errorlevel 1 (
    echo [INFO] Creating initial migration...
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
)

echo.
echo =======================================
echo         Starting ISG API Server
echo =======================================
echo.
echo 🚀 Server URL: http://localhost:8000
echo 📚 API Docs:   http://localhost:8000/docs
echo 🔑 Login:      admin@isg.com / admin123
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Server stopped.
pause