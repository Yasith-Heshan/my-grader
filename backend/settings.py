"""
Configuration settings using environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "grading_system"
    
    # Redis Configuration (for Celery)
    redis_url: str = "redis://localhost:6379/0"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Application Settings
    app_name: str = "Python Notebook Grading System"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # Security settings
    secret_key: str = "change-me-to-a-secure-random-value"
    jwt_expiration_minutes: int = 60 * 24  # 1 day by default
    
    # Docker Executor Settings
    docker_enabled: bool = True
    docker_host: Optional[str] = None
    fallback_to_local: bool = True
    require_docker: bool = False
    default_timeout: int = 10
    default_memory_limit: str = "256m"
    default_cpu_quota: int = 50000
    max_concurrent_containers: int = 10
    container_cleanup_delay: int = 5
    container_auto_remove: bool = True
    network_disabled: bool = True
    read_only_rootfs: bool = True
    max_output_size: int = 10240
    python_docker_image: str = "grader-python-sandbox:latest"
    log_execution_details: bool = True
    log_student_code: bool = False
    execution_pool_size: int = 5
    enable_caching: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


# Initialize settings
try:
    settings = Settings()
    print(f"✅ Settings loaded: mongodb_url={settings.mongodb_url}, db={settings.database_name}")
except Exception as e:
    print(f"❌ Failed to load settings: {e}")
    import traceback
    traceback.print_exc()
    settings = None
