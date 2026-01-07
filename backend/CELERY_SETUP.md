# Celery Setup Guide

## Prerequisites

1. **Redis** - Message broker for Celery
2. **Python packages** - Already added to requirements.txt

## Installation

### Step 1: Install Redis

#### Windows:
Download and install Redis from: https://github.com/microsoftarchive/redis/releases
Or use Windows Subsystem for Linux (WSL) or Docker:

```powershell
# Using Docker (easiest):
docker run -d -p 6379:6379 redis:latest

# Or download Windows build from:
# https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi
```

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

### Step 2: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Running the System

You need to run **3 separate processes**:

### Terminal 1: Redis Server
```bash
# If using Docker:
docker run -d -p 6379:6379 redis:latest

# If installed locally:
redis-server

# Windows (if installed as service):
# Redis should start automatically, or run:
redis-server.exe
```

### Terminal 2: FastAPI Backend
```bash
cd backend
python main.py
```

### Terminal 3: Celery Worker
```bash
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

**Note for Windows**: Use `--pool=solo` or `--pool=threads` on Windows as the default pool doesn't work.

## Verifying Setup

1. **Check Redis is running**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Check Celery worker is connected**:
   - Look for "celery@hostname ready" in the Celery worker terminal

3. **Create a Docker image** in the UI:
   - The task will be queued to Celery
   - Watch the Celery worker terminal for build logs
   - Status updates in database will persist even if backend restarts

## Benefits of Celery Setup

✅ **Persistent tasks** - Tasks survive server restarts
✅ **Retry mechanism** - Automatic retry on failure (up to 3 times)
✅ **Scalability** - Can run multiple workers
✅ **Monitoring** - Better visibility into long-running tasks
✅ **Resource isolation** - Docker builds don't block API requests
✅ **Task queue** - Handle multiple build requests efficiently

## Troubleshooting

### Redis connection error:
- Make sure Redis is running on port 6379
- Check `settings.py` - redis_url should be `redis://localhost:6379/0`

### Celery won't start:
- On Windows, use: `celery -A celery_app worker --loglevel=info --pool=solo`
- Make sure you're in the `backend` directory

### Tasks not executing:
- Check Celery worker terminal for errors
- Verify database connection in worker logs
- Check image status in database: should show "pending" → "building" → "uploaded"

## Production Deployment

For production, consider:
- **Redis persistence** - Configure Redis to persist to disk
- **Celery monitoring** - Use Flower for monitoring: `pip install flower && celery -A celery_app flower`
- **Multiple workers** - Scale workers: `celery -A celery_app worker --concurrency=4`
- **Systemd/supervisord** - Auto-start services on server boot

## Configuration

Edit `backend/settings.py` to customize:
```python
redis_url: str = "redis://localhost:6379/0"  # Change for remote Redis
```

Edit `backend/celery_app.py` to customize:
- Task timeout (default: 1 hour)
- Retry behavior
- Worker settings
