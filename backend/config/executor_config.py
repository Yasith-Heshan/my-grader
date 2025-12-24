"""
Configuration for code execution engines
"""
from typing import Dict, Any
import os


class ExecutorConfig:
    """Global executor configuration"""
    
    # Docker Executor Settings
    DOCKER_ENABLED: bool = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    DOCKER_HOST: str = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")  # Unix/Linux/Mac
    # For Windows: "npipe:////./pipe/docker_engine" or "tcp://localhost:2375"
    
    # Fallback behavior
    FALLBACK_TO_LOCAL: bool = os.getenv("FALLBACK_TO_LOCAL", "true").lower() == "true"
    REQUIRE_DOCKER: bool = os.getenv("REQUIRE_DOCKER", "false").lower() == "true"
    
    # Default execution limits
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10"))  # seconds
    DEFAULT_MEMORY_LIMIT: str = os.getenv("DEFAULT_MEMORY_LIMIT", "256m")
    DEFAULT_CPU_QUOTA: int = int(os.getenv("DEFAULT_CPU_QUOTA", "50000"))  # 50% of one core
    
    # Container management
    MAX_CONCURRENT_CONTAINERS: int = int(os.getenv("MAX_CONCURRENT_CONTAINERS", "10"))
    CONTAINER_CLEANUP_DELAY: int = int(os.getenv("CONTAINER_CLEANUP_DELAY", "5"))  # seconds
    CONTAINER_AUTO_REMOVE: bool = os.getenv("CONTAINER_AUTO_REMOVE", "true").lower() == "true"
    
    # Security settings
    NETWORK_DISABLED: bool = os.getenv("NETWORK_DISABLED", "true").lower() == "true"
    READ_ONLY_ROOTFS: bool = os.getenv("READ_ONLY_ROOTFS", "true").lower() == "true"
    MAX_OUTPUT_SIZE: int = int(os.getenv("MAX_OUTPUT_SIZE", "10240"))  # bytes
    
    # Docker images for different languages
    DOCKER_IMAGES: Dict[str, str] = {
        "python": os.getenv("PYTHON_DOCKER_IMAGE", "grader-python-sandbox:latest"),
        "javascript": os.getenv("JS_DOCKER_IMAGE", "grader-js-sandbox:latest"),
        "java": os.getenv("JAVA_DOCKER_IMAGE", "grader-java-sandbox:latest"),
    }
    
    # Language-specific configurations
    PYTHON_VERSION: str = os.getenv("PYTHON_VERSION", "3.11")
    ALLOWED_PYTHON_IMPORTS: list = [
        "math", "random", "datetime", "json", "re", "collections",
        "itertools", "functools", "operator", "string", "decimal",
        "fractions", "statistics", "typing"
    ]
    
    # Logging
    LOG_EXECUTION_DETAILS: bool = os.getenv("LOG_EXECUTION_DETAILS", "true").lower() == "true"
    LOG_STUDENT_CODE: bool = os.getenv("LOG_STUDENT_CODE", "false").lower() == "true"
    
    # Performance
    EXECUTION_POOL_SIZE: int = int(os.getenv("EXECUTION_POOL_SIZE", "5"))
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "false").lower() == "true"
    
    @classmethod
    def get_docker_image(cls, language: str) -> str:
        """Get Docker image for a specific language"""
        return cls.DOCKER_IMAGES.get(language.lower(), cls.DOCKER_IMAGES["python"])
    
    @classmethod
    def is_docker_available(cls) -> bool:
        """Check if Docker is enabled and should be used"""
        return cls.DOCKER_ENABLED
    
    @classmethod
    def should_fallback(cls) -> bool:
        """Check if fallback to local execution is allowed"""
        return cls.FALLBACK_TO_LOCAL and not cls.REQUIRE_DOCKER
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if cls.DEFAULT_TIMEOUT <= 0 or cls.DEFAULT_TIMEOUT > 300:
            errors.append("DEFAULT_TIMEOUT must be between 1 and 300 seconds")
        
        if cls.DEFAULT_CPU_QUOTA <= 0 or cls.DEFAULT_CPU_QUOTA > 400000:
            errors.append("DEFAULT_CPU_QUOTA must be between 1 and 400000")
        
        if cls.MAX_CONCURRENT_CONTAINERS <= 0:
            errors.append("MAX_CONCURRENT_CONTAINERS must be positive")
        
        if cls.MAX_OUTPUT_SIZE <= 0:
            errors.append("MAX_OUTPUT_SIZE must be positive")
        
        if cls.REQUIRE_DOCKER and not cls.DOCKER_ENABLED:
            errors.append("REQUIRE_DOCKER is true but DOCKER_ENABLED is false")
        
        return len(errors) == 0, errors
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "docker_enabled": cls.DOCKER_ENABLED,
            "docker_host": cls.DOCKER_HOST,
            "fallback_to_local": cls.FALLBACK_TO_LOCAL,
            "require_docker": cls.REQUIRE_DOCKER,
            "default_timeout": cls.DEFAULT_TIMEOUT,
            "default_memory_limit": cls.DEFAULT_MEMORY_LIMIT,
            "default_cpu_quota": cls.DEFAULT_CPU_QUOTA,
            "max_concurrent_containers": cls.MAX_CONCURRENT_CONTAINERS,
            "network_disabled": cls.NETWORK_DISABLED,
            "read_only_rootfs": cls.READ_ONLY_ROOTFS,
            "docker_images": cls.DOCKER_IMAGES,
            "python_version": cls.PYTHON_VERSION,
        }


# Validate configuration on import
_is_valid, _errors = ExecutorConfig.validate()
if not _is_valid:
    import warnings
    warnings.warn(f"Executor configuration validation failed: {', '.join(_errors)}")
