"""
Executor factory for creating appropriate code executors
"""
import logging
from typing import Optional

from .executor_interface import CodeExecutor, ExecutionConfig, ExecutionLanguage
from .docker_executor import DockerExecutor
from .local_executor import LocalExecutor, RestrictedLocalExecutor
from config.executor_config import ExecutorConfig

logger = logging.getLogger(__name__)


class ExecutorFactory:
    """Factory for creating code executors based on configuration"""
    
    @staticmethod
    async def create_executor(
        config: Optional[ExecutionConfig] = None,
        force_docker: bool = False,
        force_local: bool = False
    ) -> CodeExecutor:
        """
        Create appropriate executor based on configuration and availability
        
        Args:
            config: Execution configuration
            force_docker: Force use of Docker executor
            force_local: Force use of local executor (dev only)
            
        Returns:
            CodeExecutor instance (Docker or Local)
            
        Raises:
            RuntimeError: If Docker is required but not available
        """
        # Check if forced
        if force_local:
            logger.warning("Local executor forced - INSECURE MODE")
            return LocalExecutor(config)
        
        # Try Docker first if enabled
        if ExecutorConfig.is_docker_available() or force_docker:
            try:
                docker_executor = DockerExecutor(config)
                
                # Verify Docker is actually available
                if await docker_executor.health_check():
                    logger.info("Using Docker executor (secure mode)")
                    return docker_executor
                else:
                    logger.warning("Docker health check failed")
                    
                    # Fall back if allowed
                    if ExecutorConfig.should_fallback():
                        logger.warning("Falling back to local executor")
                        return RestrictedLocalExecutor(config)
                    else:
                        raise RuntimeError(
                            "Docker is required but health check failed"
                        )
            
            except Exception as e:
                logger.error(f"Failed to create Docker executor: {e}")
                
                # Fall back if allowed
                if ExecutorConfig.should_fallback():
                    logger.warning("Falling back to local executor due to error")
                    return RestrictedLocalExecutor(config)
                else:
                    raise RuntimeError(
                        f"Docker is required but initialization failed: {e}"
                    ) from e
        
        # Docker disabled, use local executor
        if ExecutorConfig.should_fallback():
            logger.warning("Docker disabled, using local executor - INSECURE MODE")
            return RestrictedLocalExecutor(config)
        else:
            raise RuntimeError(
                "Docker is disabled and fallback is not allowed. "
                "Enable Docker or set FALLBACK_TO_LOCAL=true"
            )
    
    @staticmethod
    async def get_default_executor() -> CodeExecutor:
        """
        Get default executor with default configuration
        
        Returns:
            CodeExecutor instance
        """
        return await ExecutorFactory.create_executor()
    
    @staticmethod
    async def validate_setup() -> tuple[bool, list[str]]:
        """
        Validate executor setup and configuration
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
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
                    issues.append("Docker is enabled but health check failed")
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
