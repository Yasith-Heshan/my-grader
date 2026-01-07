"""
Test script to verify Celery setup
Run this after starting Redis and Celery worker
"""
import asyncio
from celery_app import celery_app
from tasks.docker_tasks import build_and_push_docker_image

def test_celery_connection():
    """Test if Celery can connect to Redis"""
    try:
        # Try to inspect active workers
        inspect = celery_app.control.inspect()
        workers = inspect.active()
        
        if workers:
            print("✓ Celery is connected!")
            print(f"✓ Active workers: {list(workers.keys())}")
            return True
        else:
            print("✗ No active Celery workers found")
            print("  Make sure to run: celery -A celery_app worker --loglevel=info --pool=solo")
            return False
            
    except Exception as e:
        print(f"✗ Failed to connect to Celery: {e}")
        print("  Make sure Redis is running on port 6379")
        return False

def test_redis_connection():
    """Test if Redis is accessible"""
    try:
        from redis import Redis
        r = Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✓ Redis is running and accessible")
        return True
    except Exception as e:
        print(f"✗ Cannot connect to Redis: {e}")
        print("  Start Redis with: docker run -d -p 6379:6379 redis:latest")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  Celery Setup Verification")
    print("=" * 50)
    print()
    
    print("[1/2] Testing Redis connection...")
    redis_ok = test_redis_connection()
    print()
    
    print("[2/2] Testing Celery connection...")
    celery_ok = test_celery_connection()
    print()
    
    print("=" * 50)
    if redis_ok and celery_ok:
        print("  ✓ All checks passed!")
        print("  System is ready for Docker image builds")
    else:
        print("  ✗ Some checks failed")
        print("  Please fix the issues above")
    print("=" * 50)
