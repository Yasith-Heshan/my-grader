# Quick Start Guide - Celery Integration

## What Changed?

Docker image building now uses **Celery + Redis** for background task processing instead of FastAPI's BackgroundTasks. This provides:

- ✅ Persistent task queue (survives server restarts)
- ✅ Automatic retry on failure
- ✅ Better monitoring and logging
- ✅ Scalable worker processes
- ✅ No blocking of API requests

## Quick Setup (3 Steps)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Redis (Choose one method)

**Option A - Using Docker (Recommended):**
```bash
# Windows:
start_redis.bat

# Linux/Mac:
docker run -d -p 6379:6379 --name redis-grader redis:latest
```

**Option B - Local Redis:**
- Download from: https://github.com/microsoftarchive/redis/releases (Windows)
- Or: `brew install redis` (Mac) / `apt install redis-server` (Linux)
- Run: `redis-server`

### 3. Start Services (Need 2 terminals)

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Celery Worker:**
```bash
cd backend

# Windows:
celery -A celery_app worker --loglevel=info --pool=solo

# Linux/Mac:
celery -A celery_app worker --loglevel=info
```

## Using the System

1. **Create Docker Image** via UI → Teacher → Docker Images
2. **Monitor Progress**:
   - Watch Celery worker terminal for build logs
   - Refresh page to see status updates
   - Status flow: pending → building → uploading → uploaded

3. **Check Status**:
   ```bash
   # In Celery worker terminal, you'll see:
   [2026-01-07 10:30:00,000: INFO/MainProcess] Task tasks.docker_tasks.build_and_push_docker_image[abc-123] received
   [2026-01-07 10:30:05,000: INFO/MainProcess] Building image: username/grader-myimage:latest
   [2026-01-07 10:32:00,000: INFO/MainProcess] Task tasks.docker_tasks.build_and_push_docker_image[abc-123] succeeded
   ```

## Troubleshooting

### Redis not connecting?
```bash
# Test Redis:
redis-cli ping
# Should return: PONG
```

### Celery worker won't start?
```bash
# Windows - must use --pool=solo:
celery -A celery_app worker --loglevel=info --pool=solo

# Check you're in the backend directory
```

### Tasks not running?
1. Check Celery worker is running (Terminal 2)
2. Check Redis is running: `docker ps | grep redis`
3. Look for errors in Celery worker terminal

### Build fails?
- Check Docker Desktop is running
- Check Celery worker terminal for error messages
- Image status will show "failed" with error message

## File Changes Summary

**New Files:**
- `backend/celery_app.py` - Celery configuration
- `backend/tasks/docker_tasks.py` - Celery tasks for Docker builds
- `backend/CELERY_SETUP.md` - Detailed setup guide
- `backend/start_redis.bat` - Redis startup script (Windows)
- `backend/start_celery_worker.bat` - Celery startup script (Windows)

**Modified Files:**
- `backend/requirements.txt` - Added celery and redis
- `backend/settings.py` - Added redis_url config
- `backend/routers/teacher.py` - Use Celery instead of BackgroundTasks

## Production Considerations

For production deployment:

1. **Redis Persistence**: Configure Redis to save to disk
2. **Multiple Workers**: Scale workers based on load
3. **Monitoring**: Install Flower for web-based monitoring
   ```bash
   pip install flower
   celery -A celery_app flower
   # Access at http://localhost:5555
   ```
4. **Process Management**: Use systemd/supervisord to auto-start services

## Need Help?

See detailed documentation in `CELERY_SETUP.md`
