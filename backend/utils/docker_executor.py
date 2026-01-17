"""
Docker-based secure code executor
Executes student code in isolated Docker containers with resource limits
"""
import docker
from docker.errors import DockerException, NotFound, APIError
from typing import Optional, Dict, Any
import json
import tempfile
import os
import time
from pathlib import Path
import logging

from .executor_interface import CodeExecutor, ExecutionConfig, ExecutionResult
from config.executor_config import ExecutorConfig

logger = logging.getLogger(__name__)


class DockerExecutor(CodeExecutor):
    """Docker-based code executor with security isolation"""
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        super().__init__(config)
        self.docker_client: Optional[docker.DockerClient] = None
        self._container_count = 0
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Docker client"""
        try:
            # Auto-detect Docker host based on platform
            if os.name == 'nt':  # Windows
                try:
                    self.docker_client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                except:
                    self.docker_client = docker.DockerClient(base_url='tcp://localhost:2375')
            else:  # Unix/Linux/Mac
                self.docker_client = docker.from_env()
            
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")
            
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None
    
    async def execute(
        self,
        student_code: str,
        test_code: str,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """Execute student code in a Docker container"""
        if not self.docker_client:
            raise RuntimeError("Docker client not available")
        
        exec_config = config_override or self.config
        
        # Check concurrent container limit
        if self._container_count >= ExecutorConfig.MAX_CONCURRENT_CONTAINERS:
            return ExecutionResult(
                success=False,
                error_message=f"Maximum concurrent containers ({ExecutorConfig.MAX_CONCURRENT_CONTAINERS}) reached",
                feedback="System is currently busy. Please try again."
            )
        
        start_time = time.time()
        container = None
        temp_dir = None
        
        try:
            # Create temporary directory with code files
            temp_dir = tempfile.mkdtemp(prefix="grader_")
            student_file = Path(temp_dir) / "student_code.py"
            test_file = Path(temp_dir) / "test_code.py"
            runner_file = Path(temp_dir) / "runner.py"
            
            student_file.write_text(student_code, encoding='utf-8')
            test_file.write_text(test_code, encoding='utf-8')
            runner_file.write_text(self._create_runner_script(), encoding='utf-8')
            
            # Get image - use custom image if specified, otherwise default
            if exec_config.custom_image:
                image = exec_config.custom_image
                logger.info(f"Using custom Docker image: {image}")
            else:
                image = ExecutorConfig.get_docker_image(exec_config.language.value)
                logger.info(f"Using default Docker image: {image}")
            
            await self._ensure_image_exists(image)
            
            # Create and run container
            self._container_count += 1
            container = await self._create_container(image, temp_dir, exec_config)
            container.start()
            
            # Wait for container with timeout
            try:
                exit_code = container.wait(timeout=exec_config.timeout)
                timeout_occurred = False
            except Exception:
                timeout_occurred = True
                exit_code = {'StatusCode': -1}
                container.stop(timeout=1)
            
            # Get logs
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
            
            # Truncate if too large
            max_size = ExecutorConfig.MAX_OUTPUT_SIZE
            if len(stdout) > max_size:
                stdout = stdout[:max_size] + "\n...(truncated)"
            if len(stderr) > max_size:
                stderr = stderr[:max_size] + "\n...(truncated)"
            
            execution_time = time.time() - start_time
            result = self._parse_results(stdout, stderr, exit_code, timeout_occurred, execution_time)
            
            if ExecutorConfig.LOG_EXECUTION_DETAILS:
                logger.info(f"Execution - Success: {result.success}, Time: {execution_time:.2f}s")
            
            return result
            
        except DockerException as e:
            logger.error(f"Docker error: {e}")
            return ExecutionResult(
                success=False,
                error_message=f"Docker error: {str(e)}",
                feedback="Error setting up execution environment"
            )
        except Exception as e:
            logger.error(f"Execution error: {e}", exc_info=True)
            return ExecutionResult(
                success=False,
                error_message=f"Execution error: {str(e)}",
                feedback="Unexpected error during execution"
            )
        finally:
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
    
    async def _create_container(self, image: str, temp_dir: str, config: ExecutionConfig) -> Any:
        """Create Docker container with security constraints"""
        volumes = {temp_dir: {'bind': '/sandbox', 'mode': 'ro'}}
        
        container_config = {
            'image': image,
            'command': ['python', '/sandbox/runner.py'],
            'volumes': volumes,
            'working_dir': '/sandbox',
            'detach': True,
            'auto_remove': False,
            'network_disabled': config.network_disabled,
            'mem_limit': config.memory_limit,
            'memswap_limit': config.memory_limit,
            'cpu_quota': config.cpu_quota,
            'cpu_period': 100000,
            'pids_limit': 50,
            'read_only': config.read_only_rootfs,
            'tmpfs': {'/tmp': 'size=10M,mode=1777'},
            'security_opt': ['no-new-privileges'],
            'cap_drop': ['ALL'],
        }
        
        # Only set user for default images that have the sandbox user
        # Custom images may not have this user, so run as root (still isolated)
        if not config.custom_image or 'grader-python-sandbox' in image:
            container_config['user'] = 'sandbox'
        
        return self.docker_client.containers.create(**container_config)

    
    def _create_runner_script(self) -> str:
        """Create Python runner script that executes student and test code"""
        return '''#!/usr/bin/env python3
import sys
import json
import traceback
from io import StringIO

def main():
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
        namespace = {}
        old_stdout, old_stderr = sys.stdout, sys.stderr
        captured_stdout, captured_stderr = StringIO(), StringIO()
        sys.stdout, sys.stderr = captured_stdout, captured_stderr
        
        try:
            with open('/sandbox/student_code.py', 'r') as f:
                exec(f.read(), namespace)
            with open('/sandbox/test_code.py', 'r') as f:
                exec(f.read(), namespace)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
        
        result["stdout"] = captured_stdout.getvalue()
        result["stderr"] = captured_stderr.getvalue()
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
        """Parse execution results from container output"""
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
        """Ensure Docker image exists, pull if necessary"""
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
                    "Please build the image first."
                ) from e
    
    async def health_check(self) -> bool:
        """Check if Docker executor is healthy"""
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
                filters = {'label': 'grader=true', 'status': 'exited'}
                for container in self.docker_client.containers.list(all=True, filters=filters):
                    try:
                        container.remove(force=True)
                        logger.info(f"Cleaned up container: {container.id[:12]}")
                    except Exception as e:
                        logger.warning(f"Failed to remove container: {e}")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
