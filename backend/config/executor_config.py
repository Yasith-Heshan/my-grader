"""
Configuration for code execution engines
"""
import os


class ExecutorConfig:
    """Global executor configuration"""
    
    # Docker settings
    DOCKER_ENABLED: bool = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    DOCKER_HOST: str = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
    FALLBACK_TO_LOCAL: bool = os.getenv("FALLBACK_TO_LOCAL", "true").lower() == "true"
    
    # Execution limits
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10"))
    DEFAULT_MEMORY_LIMIT: str = os.getenv("DEFAULT_MEMORY_LIMIT", "256m")
    DEFAULT_CPU_QUOTA: int = int(os.getenv("DEFAULT_CPU_QUOTA", "50000"))
    
    # Container management
    MAX_CONCURRENT_CONTAINERS: int = int(os.getenv("MAX_CONCURRENT_CONTAINERS", "10"))
    CONTAINER_AUTO_REMOVE: bool = os.getenv("CONTAINER_AUTO_REMOVE", "true").lower() == "true"
    
    # Security
    NETWORK_DISABLED: bool = os.getenv("NETWORK_DISABLED", "true").lower() == "true"
    READ_ONLY_ROOTFS: bool = os.getenv("READ_ONLY_ROOTFS", "true").lower() == "true"
    MAX_OUTPUT_SIZE: int = int(os.getenv("MAX_OUTPUT_SIZE", "10240"))
    
    # Docker images
    PYTHON_DOCKER_IMAGE: str = os.getenv("PYTHON_DOCKER_IMAGE", "grader-python-sandbox:latest")
    
    # Logging
    LOG_EXECUTION_DETAILS: bool = os.getenv("LOG_EXECUTION_DETAILS", "true").lower() == "true"
    
    @classmethod
    def get_docker_image(cls, language: str = "python") -> str:
        """Get Docker image for language"""
        return cls.PYTHON_DOCKER_IMAGE
    
    @classmethod
    def is_docker_available(cls) -> bool:
        """Check if Docker is enabled"""
        return cls.DOCKER_ENABLED
    
    @classmethod
    def should_fallback(cls) -> bool:
        """Check if fallback to local execution is allowed"""
        return cls.FALLBACK_TO_LOCAL
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """Validate configuration"""
        errors = []
        
        if cls.DEFAULT_TIMEOUT <= 0 or cls.DEFAULT_TIMEOUT > 300:
            errors.append("DEFAULT_TIMEOUT must be 1-300 seconds")
        
        if cls.MAX_CONCURRENT_CONTAINERS <= 0:
            errors.append("MAX_CONCURRENT_CONTAINERS must be positive")
        
        if cls.MAX_OUTPUT_SIZE <= 0:
            errors.append("MAX_OUTPUT_SIZE must be positive")
        
        return len(errors) == 0, errors
