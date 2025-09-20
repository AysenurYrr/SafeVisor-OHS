@echo off
echo ================================
echo    Stopping ISG API Services
echo ================================
echo.

echo Stopping Docker Compose services...
docker compose down

if %errorlevel% equ 0 (
    echo.
    echo ✅ Services stopped successfully!
    echo.
    echo To completely remove data volumes, run:
    echo    docker compose down -v
    echo.
    echo To restart services, run:
    echo    docker-run.bat
) else (
    echo.
    echo ❌ Error stopping services
    echo Please check Docker Desktop is running
)

echo.
pause