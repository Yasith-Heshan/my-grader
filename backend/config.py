"""
Configuration settings using environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "grading_system"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
