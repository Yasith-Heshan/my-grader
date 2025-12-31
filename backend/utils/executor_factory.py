"""
Executor factory for creating code executors
"""
import logging
from typing import Optional

from .executor_interface import CodeExecutor, ExecutionConfig
from .docker_executor import DockerExecutor
from .local_executor import RestrictedLocalExecutor
from config.executor_config import ExecutorConfig

logger = logging.getLogger(__name__)


class ExecutorFactory:
    """Factory for creating code executors"""
    
    @staticmethod
    async def create_executor(config: Optional[ExecutionConfig] = None) -> CodeExecutor:
        """
        Create executor based on configuration
        
        Args:
            config: Execution configuration
            
        Returns:
            CodeExecutor instance (Docker or Local fallback)
        """
        # Try Docker first if enabled
        if ExecutorConfig.is_docker_available():
            try:
                docker_executor = DockerExecutor(config)
                if await docker_executor.health_check():
                    logger.info("Using Docker executor (secure)")
                    return docker_executor
                logger.warning("Docker health check failed")
            except Exception as e:
                logger.error(f"Docker initialization failed: {e}")
        
        # Fall back to local executor if allowed
        if ExecutorConfig.should_fallback():
            logger.warning("Using local executor - DEVELOPMENT MODE ONLY")
            return RestrictedLocalExecutor(config)
        
        raise RuntimeError(
            "Docker unavailable and fallback disabled. "
            "Enable Docker or set FALLBACK_TO_LOCAL=true"
        )
    
    @staticmethod
    async def get_default_executor() -> CodeExecutor:
        """Get default executor with default configuration"""
        return await ExecutorFactory.create_executor()
    
    @staticmethod
    async def validate_setup() -> tuple[bool, list[str]]:
        """Validate executor setup and configuration"""
        issues = []
        
        # Validate configuration
        config_valid, config_errors = ExecutorConfig.validate()
        if not config_valid:
            issues.extend(config_errors)
        
        # Check Docker availability
        if ExecutorConfig.is_docker_available():
            try:
                docker_executor = DockerExecutor()
                if not await docker_executor.health_check():
                    issues.append("Docker health check failed")
                await docker_executor.cleanup()
            except Exception as e:
                issues.append(f"Docker initialization failed: {e}")
        
        # Check if any executor is available
        try:
            executor = await ExecutorFactory.get_default_executor()
            await executor.cleanup()
        except Exception as e:
            issues.append(f"No working executor available: {e}")
        
        return len(issues) == 0, issues
