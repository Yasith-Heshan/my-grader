"""
Celery application configuration
"""
from celery import Celery
from settings import settings

# Create Celery app
celery_app = Celery(
    "grader",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['tasks.docker_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_max_tasks_per_child=50,
)

if __name__ == '__main__':
    celery_app.start()
