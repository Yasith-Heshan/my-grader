@echo off
echo Starting Celery Worker for Docker Image Building...
echo.
echo Make sure Redis is running on port 6379
echo.

cd /d "%~dp0"
celery -A celery_app worker --loglevel=info --pool=solo

pause
