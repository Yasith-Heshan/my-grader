@echo off
echo Starting Redis Server using Docker...
echo.
echo This will:
echo   1. Pull Redis image if not present
echo   2. Run Redis on port 6379
echo   3. Run in background (detached mode)
echo.

docker run -d -p 6379:6379 --name redis-grader redis:latest

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Redis started successfully!
    echo   - Running on: localhost:6379
    echo   - Container name: redis-grader
    echo.
    echo To stop Redis: docker stop redis-grader
    echo To restart: docker start redis-grader
    echo To remove: docker rm -f redis-grader
) else (
    echo.
    echo ✗ Failed to start Redis
    echo   Make sure Docker Desktop is running
)

pause
