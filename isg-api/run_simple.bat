@echo off
REM Simple ISG API Startup Script for Windows

echo Starting ISG Safety API (Simple Version)...
echo.

REM Test Python command
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies using the command from your attachment
echo Installing dependencies...
pip install fastapi uvicorn[standard] psycopg2-binary sqlalchemy alembic python-jose[cryptography] passlib[bcrypt] pydantic-settings

REM Also install additional dependencies
pip install python-multipart email-validator argon2-cffi python-dateutil

REM Create simple .env file
if not exist ".env" (
    echo Creating .env file...
    echo DATABASE_URL=sqlite:///./isg.db > .env
    echo SECRET_KEY=your-secret-key-change-this >> .env
    echo BACKEND_CORS_ORIGINS=["http://localhost:5173"] >> .env
)

echo.
echo Starting server at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

REM Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause