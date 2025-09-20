@echo off
echo ================================
echo    ISG API Docker Setup
echo ================================
echo.

echo Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Checking Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not available
    echo Please ensure Docker Desktop is running
    pause
    exit /b 1
)

echo.
echo Starting ISG API services...
echo.

REM Create pgdata directory if it doesn't exist
if not exist "pgdata" mkdir pgdata

REM Start the services
docker compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ Services started successfully!
    echo.
    echo 📊 pgAdmin: http://localhost:5050
    echo    - Email: admin@isg.com
    echo    - Password: admin
    echo.
    echo 🗄️  PostgreSQL: postgresql://isg:devpass@localhost:5432/isgdb
    echo.
    echo 🔄 To run the API locally with hot-reload:
    echo    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    echo.
    echo 📱 API will be available at: http://localhost:8000
    echo 📚 API Documentation: http://localhost:8000/docs
    echo.
    echo To stop services: docker compose down
    echo To reset database: docker compose down -v
) else (
    echo.
    echo ❌ Failed to start services
    echo Please check Docker Desktop is running and try again
)

echo.
pause