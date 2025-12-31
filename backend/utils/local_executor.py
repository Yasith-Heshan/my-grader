"""
Local code executor for development mode (INSECURE - DEV ONLY)

WARNING: Only use in development. Never in production.
"""
import sys
import traceback
import time
from io import StringIO
from typing import Optional
import logging
import signal
from contextlib import contextmanager

from .executor_interface import CodeExecutor, ExecutionConfig, ExecutionResult

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    """Exception raised when code execution times out"""
    pass


@contextmanager
def time_limit(seconds: int):
    """Context manager to limit execution time (Unix/Linux/Mac only)"""
    def signal_handler(signum, frame):
        raise TimeoutException("Code execution timed out")
    
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:
        logger.warning("Timeout not enforced on Windows in local executor")
        yield


class LocalExecutor(CodeExecutor):
    """
    Local code executor for development mode
    
    WARNING: INSECURE - only for development
    - No process isolation
    - Can access file system and network
    - No memory limits
    """
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        super().__init__(config)
        logger.warning("LocalExecutor initialized - INSECURE MODE. Development only!")
    
    async def execute(
        self,
        student_code: str,
        test_code: str,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """Execute student code locally (INSECURE)"""
        exec_config = config_override or self.config
        start_time = time.time()
        namespace = {}
        captured_stdout = ""
        captured_stderr = ""
        timeout_occurred = False
        
        try:
            old_stdout, old_stderr = sys.stdout, sys.stderr
            stdout_buffer, stderr_buffer = StringIO(), StringIO()
            sys.stdout, sys.stderr = stdout_buffer, stderr_buffer
            
            try:
                with time_limit(exec_config.timeout):
                    exec(student_code, namespace)
                    exec(test_code, namespace)
            except TimeoutException:
                timeout_occurred = True
                logger.warning(f"Code execution timed out after {exec_config.timeout}s")
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr
                captured_stdout = stdout_buffer.getvalue()
                captured_stderr = stderr_buffer.getvalue()
            
            execution_time = time.time() - start_time
            
            if timeout_occurred:
                return ExecutionResult(
                    success=False,
                    stdout=captured_stdout,
                    stderr=captured_stderr,
                    execution_time=execution_time,
                    timeout_occurred=True,
                    error_message="Execution timed out",
                    feedback=f"Code execution exceeded time limit ({exec_config.timeout}s)"
                )
            
            # Extract results
            passed = namespace.get('passed', False)
            score = namespace.get('score', 0.0)
            max_score = namespace.get('max_score', 0.0)
            feedback = namespace.get('feedback', 'Test completed')
            test_results = namespace.get('test_results', [])
            
            # Truncate output
            max_output = 10240
            if len(captured_stdout) > max_output:
                captured_stdout = captured_stdout[:max_output] + "\n...(truncated)"
            if len(captured_stderr) > max_output:
                captured_stderr = captured_stderr[:max_output] + "\n...(truncated)"
            
            return ExecutionResult(
                success=True,
                passed=passed,
                score=score,
                max_score=max_score,
                stdout=captured_stdout,
                stderr=captured_stderr,
                exit_code=0,
                execution_time=execution_time,
                feedback=feedback,
                test_results=test_results
            )
        
        except Exception as e:
            sys.stdout, sys.stderr = old_stdout, old_stderr
            execution_time = time.time() - start_time
            error_trace = traceback.format_exc()
            logger.error(f"Error during local execution: {e}", exc_info=True)
            
            return ExecutionResult(
                success=False,
                stdout=captured_stdout,
                stderr=captured_stderr + "\n" + error_trace,
                exit_code=1,
                execution_time=execution_time,
                error_message=str(e),
                feedback=f"Error during execution: {str(e)}"
            )
    
    async def health_check(self) -> bool:
        """Check if local executor is ready"""
        return True
    
    async def cleanup(self):
        """Clean up resources"""
        pass


class RestrictedLocalExecutor(LocalExecutor):
    """
    Restricted local executor with basic safety checks
    
    Still INSECURE - only for development
    """
    
    DANGEROUS_IMPORTS = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'eval', 'exec', 'compile', '__import__', 'open', 'file'
    }
    
    DANGEROUS_KEYWORDS = [
        '__import__', 'eval(', 'exec(', 'compile(',
        'os.system', 'subprocess.', 'socket.', 'open('
    ]
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        super().__init__(config)
        logger.info("RestrictedLocalExecutor initialized - Some safety checks enabled")
    
    async def execute(
        self,
        student_code: str,
        test_code: str,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """Execute with basic safety checks"""
        validation_error = self._validate_code(student_code)
        if validation_error:
            return ExecutionResult(
                success=False,
                error_message=validation_error,
                feedback=f"Code validation failed: {validation_error}"
            )
        
        return await super().execute(student_code, test_code, config_override)
    
    def _validate_code(self, code: str) -> Optional[str]:
        """Validate code for obvious security issues"""
        code_lower = code.lower()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword.lower() in code_lower:
                return f"Forbidden operation: {keyword}"
        
        # Check imports
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                parts = line.split()
                if len(parts) >= 2:
                    module = parts[1].split('.')[0]
                    if module in self.DANGEROUS_IMPORTS:
                        return f"Forbidden import: {module}"
        
        return None
