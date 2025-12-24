"""
Docker-based secure code executor
Executes student code in isolated Docker containers with resource limits
"""
import asyncio
import docker
from docker.errors import DockerException, NotFound, APIError
from typing import Optional, Dict, Any
import json
import tempfile
import os
import time
from pathlib import Path
import logging

from .executor_interface import (
    CodeExecutor, ExecutionConfig, ExecutionResult, ExecutionLanguage
)
from config.executor_config import ExecutorConfig

logger = logging.getLogger(__name__)


class DockerExecutor(CodeExecutor):
    """
    Docker-based code executor with security isolation
    
    Features:
    - Process isolation via containers
    - Resource limits (CPU, memory, timeout)
    - Network isolation
    - Read-only filesystem
    - Automatic cleanup
    """
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        """
        Initialize Docker executor
        
        Args:
            config: Execution configuration
        """
        super().__init__(config)
        self.docker_client: Optional[docker.DockerClient] = None
        self._container_count = 0
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Docker client"""
        try:
            # Auto-detect Docker host based on platform
            if os.name == 'nt':  # Windows
                # Try npipe first, fall back to TCP
                try:
                    self.docker_client = docker.DockerClient(
                        base_url='npipe:////./pipe/docker_engine'
                    )
                except:
                    self.docker_client = docker.DockerClient(
                        base_url='tcp://localhost:2375'
                    )
            else:  # Unix/Linux/Mac
                self.docker_client = docker.from_env()
            
            # Verify connection
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")
            
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None
            if ExecutorConfig.REQUIRE_DOCKER:
                raise RuntimeError(
                    "Docker is required but not available. "
                    "Please ensure Docker is installed and running."
                ) from e
    
    async def execute(
        self,
        student_code: str,
        test_code: str,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """
        Execute student code in a Docker container
        
        Args:
            student_code: Student's submitted code
            test_code: Test/grading code
            config_override: Optional configuration override
            
        Returns:
            ExecutionResult with execution details
        """
        if not self.docker_client:
            raise RuntimeError(
                "Docker client not available. Cannot execute code."
            )
        
        # Use override config if provided
        exec_config = config_override or self.config
        
        # Check concurrent container limit
        if self._container_count >= ExecutorConfig.MAX_CONCURRENT_CONTAINERS:
            return ExecutionResult(
                success=False,
                error_message=f"Maximum concurrent containers ({ExecutorConfig.MAX_CONCURRENT_CONTAINERS}) reached",
                feedback="System is currently busy. Please try again in a moment."
            )
        
        start_time = time.time()
        container = None
        temp_dir = None
        
        try:
            # Create temporary directory for code files
            temp_dir = tempfile.mkdtemp(prefix="grader_")
            
            # Write code files
            student_file = Path(temp_dir) / "student_code.py"
            test_file = Path(temp_dir) / "test_code.py"
            runner_file = Path(temp_dir) / "runner.py"
            
            student_file.write_text(student_code, encoding='utf-8')
            test_file.write_text(test_code, encoding='utf-8')
            
            # Create runner script that executes both files
            runner_script = self._create_runner_script(exec_config)
            runner_file.write_text(runner_script, encoding='utf-8')
            
            # Get Docker image
            image = ExecutorConfig.get_docker_image(exec_config.language.value)
            
            # Ensure image exists
            await self._ensure_image_exists(image)
            
            # Create and run container
            self._container_count += 1
            container = await self._create_container(
                image=image,
                temp_dir=temp_dir,
                config=exec_config
            )
            
            # Start container
            container.start()
            
            # Wait for container with timeout
            try:
                exit_code = container.wait(timeout=exec_config.timeout)
                timeout_occurred = False
            except Exception:
                # Timeout occurred
                timeout_occurred = True
                exit_code = {'StatusCode': -1}
                container.stop(timeout=1)
            
            # Get logs
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
            
            # Truncate output if too large
            if len(stdout) > ExecutorConfig.MAX_OUTPUT_SIZE:
                stdout = stdout[:ExecutorConfig.MAX_OUTPUT_SIZE] + "\n... (output truncated)"
            if len(stderr) > ExecutorConfig.MAX_OUTPUT_SIZE:
                stderr = stderr[:ExecutorConfig.MAX_OUTPUT_SIZE] + "\n... (output truncated)"
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Parse results from stdout (JSON format expected)
            result = self._parse_results(stdout, stderr, exit_code, timeout_occurred, execution_time)
            
            if ExecutorConfig.LOG_EXECUTION_DETAILS:
                logger.info(
                    f"Execution completed - Success: {result.success}, "
                    f"Time: {execution_time:.2f}s, Exit: {exit_code.get('StatusCode', -1)}"
                )
            
            return result
            
        except DockerException as e:
            logger.error(f"Docker error during execution: {e}")
            return ExecutionResult(
                success=False,
                error_message=f"Docker error: {str(e)}",
                feedback="An error occurred while setting up the execution environment."
            )
        
        except Exception as e:
            logger.error(f"Unexpected error during execution: {e}", exc_info=True)
            return ExecutionResult(
                success=False,
                error_message=f"Execution error: {str(e)}",
                feedback="An unexpected error occurred during code execution."
            )
        
        finally:
            # Cleanup
            self._container_count -= 1
            if container:
                try:
                    container.remove(force=True)
                except Exception as e:
                    logger.warning(f"Failed to remove container: {e}")
            
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {e}")
    
    async def _create_container(
        self,
        image: str,
        temp_dir: str,
        config: ExecutionConfig
    ) -> Any:
        """
        Create Docker container with security constraints
        
        Args:
            image: Docker image name
            temp_dir: Temporary directory with code files
            config: Execution configuration
            
        Returns:
            Docker container object
        """
        # Mount temporary directory as read-only volume
        volumes = {
            temp_dir: {
                'bind': '/sandbox',
                'mode': 'ro'  # Read-only
            }
        }
        
        # Security and resource limits
        container_config = {
            'image': image,
            'command': ['python', '/sandbox/runner.py'],
            'volumes': volumes,
            'working_dir': '/sandbox',
            'detach': True,
            'auto_remove': False,  # We'll remove manually for better control
            'network_disabled': config.network_disabled,
            'mem_limit': config.memory_limit,
            'memswap_limit': config.memory_limit,  # Disable swap
            'cpu_quota': config.cpu_quota,
            'cpu_period': 100000,  # Standard period
            'pids_limit': 50,  # Limit number of processes
            'read_only': config.read_only_rootfs,
            'tmpfs': {
                '/tmp': 'size=10M,mode=1777'  # Small writable tmp
            },
            'security_opt': ['no-new-privileges'],  # Prevent privilege escalation
            'cap_drop': ['ALL'],  # Drop all capabilities
            'user': 'sandbox',  # Run as non-root user
        }
        
        # Create container
        container = self.docker_client.containers.create(**container_config)
        
        return container
    
    def _create_runner_script(self, config: ExecutionConfig) -> str:
        """
        Create Python runner script that executes student and test code
        
        Args:
            config: Execution configuration
            
        Returns:
            Python script as string
        """
        return '''#!/usr/bin/env python3
"""
Runner script for safe code execution
Executes student code and test code, returns results as JSON
"""
import sys
import json
import traceback
from io import StringIO

def main():
    """Execute student and test code safely"""
    result = {
        "success": False,
        "passed": False,
        "score": 0.0,
        "max_score": 0.0,
        "stdout": "",
        "stderr": "",
        "feedback": "",
        "test_results": []
    }
    
    try:
        # Create namespace for execution
        namespace = {}
        
        # Capture stdout
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        captured_stdout = StringIO()
        captured_stderr = StringIO()
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr
        
        try:
            # Execute student code
            with open('/sandbox/student_code.py', 'r') as f:
                student_code = f.read()
            exec(student_code, namespace)
            
            # Execute test code
            with open('/sandbox/test_code.py', 'r') as f:
                test_code = f.read()
            exec(test_code, namespace)
            
        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        # Get captured output
        result["stdout"] = captured_stdout.getvalue()
        result["stderr"] = captured_stderr.getvalue()
        
        # Get test results from namespace
        result["success"] = True
        result["passed"] = namespace.get('passed', False)
        result["score"] = namespace.get('score', 0.0)
        result["max_score"] = namespace.get('max_score', 0.0)
        result["feedback"] = namespace.get('feedback', 'Test completed')
        result["test_results"] = namespace.get('test_results', [])
        
    except Exception as e:
        result["success"] = False
        result["stderr"] = traceback.format_exc()
        result["feedback"] = f"Error during execution: {str(e)}"
    
    # Output results as JSON
    print("###GRADER_RESULTS###")
    print(json.dumps(result, indent=2))
    print("###GRADER_RESULTS_END###")

if __name__ == '__main__':
    main()
'''
    
    def _parse_results(
        self,
        stdout: str,
        stderr: str,
        exit_code: Dict[str, int],
        timeout_occurred: bool,
        execution_time: float
    ) -> ExecutionResult:
        """
        Parse execution results from container output
        
        Args:
            stdout: Standard output
            stderr: Standard error
            exit_code: Container exit code
            timeout_occurred: Whether timeout occurred
            execution_time: Execution time in seconds
            
        Returns:
            ExecutionResult object
        """
        if timeout_occurred:
            return ExecutionResult(
                success=False,
                stdout=stdout,
                stderr=stderr,
                exit_code=-1,
                execution_time=execution_time,
                timeout_occurred=True,
                error_message="Execution timed out",
                feedback=f"Code execution exceeded time limit ({self.config.timeout}s)"
            )
        
        # Try to extract JSON results
        try:
            if "###GRADER_RESULTS###" in stdout:
                # Extract JSON between markers
                start = stdout.find("###GRADER_RESULTS###") + len("###GRADER_RESULTS###")
                end = stdout.find("###GRADER_RESULTS_END###")
                
                if end > start:
                    json_str = stdout[start:end].strip()
                    data = json.loads(json_str)
                    
                    return ExecutionResult(
                        success=data.get("success", False),
                        passed=data.get("passed", False),
                        score=data.get("score", 0.0),
                        max_score=data.get("max_score", 0.0),
                        stdout=data.get("stdout", ""),
                        stderr=data.get("stderr", ""),
                        exit_code=exit_code.get('StatusCode', 0),
                        execution_time=execution_time,
                        feedback=data.get("feedback", ""),
                        test_results=data.get("test_results", [])
                    )
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse results JSON: {e}")
        
        # Fallback: return raw output
        return ExecutionResult(
            success=exit_code.get('StatusCode', 1) == 0,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code.get('StatusCode', 1),
            execution_time=execution_time,
            feedback="Execution completed but results could not be parsed"
        )
    
    async def _ensure_image_exists(self, image: str):
        """
        Ensure Docker image exists, pull if necessary
        
        Args:
            image: Docker image name
        """
        try:
            self.docker_client.images.get(image)
        except NotFound:
            logger.info(f"Docker image '{image}' not found, pulling...")
            try:
                self.docker_client.images.pull(image)
                logger.info(f"Successfully pulled image '{image}'")
            except APIError as e:
                logger.error(f"Failed to pull image '{image}': {e}")
                raise RuntimeError(
                    f"Docker image '{image}' not found and could not be pulled. "
                    "Please build the image first using 'docker build'."
                ) from e
    
    async def health_check(self) -> bool:
        """
        Check if Docker executor is healthy
        
        Returns:
            True if Docker is available and responsive
        """
        if not self.docker_client:
            return False
        
        try:
            self.docker_client.ping()
            return True
        except Exception as e:
            logger.error(f"Docker health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Clean up Docker resources"""
        if self.docker_client:
            try:
                # Remove any dangling containers (shouldn't happen normally)
                filters = {'label': 'grader=true', 'status': 'exited'}
                for container in self.docker_client.containers.list(all=True, filters=filters):
                    try:
                        container.remove(force=True)
                        logger.info(f"Cleaned up dangling container: {container.id[:12]}")
                    except Exception as e:
                        logger.warning(f"Failed to remove container {container.id[:12]}: {e}")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
