@echo off
title Grader System - Complete Startup
color 0A

echo ========================================
echo   Python Grader System - Startup
echo ========================================
echo.

REM Check Docker
echo [1/4] Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   ✗ Docker not found! Please install Docker Desktop.
    pause
    exit /b 1
)
echo   ✓ Docker is installed

REM Start Redis
echo.
echo [2/4] Starting Redis...
docker ps | findstr redis-grader >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ✓ Redis is already running
) else (
    docker start redis-grader >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo   Starting new Redis container...
        docker run -d -p 6379:6379 --name redis-grader redis:latest >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo   ✓ Redis started successfully
        ) else (
            echo   ✗ Failed to start Redis
            pause
            exit /b 1
        )
    ) else (
        echo   ✓ Redis restarted successfully
    )
)

REM Check Python
echo.
echo [3/4] Checking Python environment...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   ✗ Python not found!
    pause
    exit /b 1
)
echo   ✓ Python is available

REM Check MongoDB
echo.
echo [4/4] Checking MongoDB...
echo   (Assuming MongoDB is running on localhost:27017)
echo   If not, please start MongoDB separately

echo.
echo ========================================
echo   All prerequisites ready!
echo ========================================
echo.
echo Next steps:
echo   1. Open 3 separate terminals (or use this window)
echo.
echo   Terminal 1 - FastAPI Backend:
echo      cd backend ^&^& python main.py
echo.
echo   Terminal 2 - Celery Worker:
echo      cd backend ^&^& celery -A celery_app worker --loglevel=info --pool=solo
echo.
echo   Terminal 3 - Frontend (optional):
echo      cd frontend ^&^& npm run dev
echo.
echo Press any key to exit...
pause >nul
