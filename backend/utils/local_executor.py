"""
Local code executor for development mode (INSECURE - DEV ONLY)
Executes code directly in the current process without isolation

WARNING: This executor should ONLY be used in development environments.
         Never use in production as it poses serious security risks.
"""
import asyncio
import sys
import traceback
import time
from io import StringIO
from typing import Optional
import logging
import signal
from contextlib import contextmanager

from .executor_interface import (
    CodeExecutor, ExecutionConfig, ExecutionResult, ExecutionLanguage
)

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    """Exception raised when code execution times out"""
    pass


@contextmanager
def time_limit(seconds: int):
    """
    Context manager to limit execution time
    Note: Only works on Unix/Linux/Mac, not Windows
    """
    def signal_handler(signum, frame):
        raise TimeoutException("Code execution timed out")
    
    if hasattr(signal, 'SIGALRM'):
        # Unix/Linux/Mac
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:
        # Windows - no timeout enforcement
        logger.warning("Timeout not enforced on Windows in local executor")
        yield


class LocalExecutor(CodeExecutor):
    """
    Local code executor for development mode
    
    WARNING: This executor is INSECURE and should only be used for development.
    It executes code directly in the current process without proper isolation.
    
    Features:
    - Fast execution (no container overhead)
    - Limited timeout support (Unix only)
    - No memory limits
    - No process isolation
    - Useful for rapid development and testing
    
    Security Risks:
    - Can access file system
    - Can access network
    - Can execute arbitrary system commands
    - Can affect the main process
    - No resource limits
    """
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        """
        Initialize local executor
        
        Args:
            config: Execution configuration
        """
        super().__init__(config)
        logger.warning(
            "LocalExecutor initialized - INSECURE MODE. "
            "Only use for development. Never use in production!"
        )
    
    async def execute(
        self,
        student_code: str,
        test_code: str,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """
        Execute student code locally (INSECURE)
        
        Args:
            student_code: Student's submitted code
            test_code: Test/grading code
            config_override: Optional configuration override
            
        Returns:
            ExecutionResult with execution details
        """
        # Use override config if provided
        exec_config = config_override or self.config
        
        start_time = time.time()
        namespace = {}
        captured_stdout = ""
        captured_stderr = ""
        timeout_occurred = False
        
        try:
            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_buffer = StringIO()
            stderr_buffer = StringIO()
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer
            
            try:
                # Execute with timeout (Unix only)
                with time_limit(exec_config.timeout):
                    # Execute student code
                    exec(student_code, namespace)
                    
                    # Execute test code
                    exec(test_code, namespace)
                
            except TimeoutException:
                timeout_occurred = True
                logger.warning(f"Code execution timed out after {exec_config.timeout}s")
            
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                captured_stdout = stdout_buffer.getvalue()
                captured_stderr = stderr_buffer.getvalue()
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Handle timeout
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
            
            # Extract results from namespace
            passed = namespace.get('passed', False)
            score = namespace.get('score', 0.0)
            max_score = namespace.get('max_score', 0.0)
            feedback = namespace.get('feedback', 'Test completed')
            test_results = namespace.get('test_results', [])
            
            # Truncate output if too large
            max_output = 10240  # 10KB
            if len(captured_stdout) > max_output:
                captured_stdout = captured_stdout[:max_output] + "\n... (output truncated)"
            if len(captured_stderr) > max_output:
                captured_stderr = captured_stderr[:max_output] + "\n... (output truncated)"
            
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
            # Restore stdout/stderr if not already done
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
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
        """
        Check if local executor is ready
        
        Returns:
            Always returns True (local execution is always available)
        """
        return True
    
    async def cleanup(self):
        """Clean up resources (no-op for local executor)"""
        pass


class RestrictedLocalExecutor(LocalExecutor):
    """
    Slightly more restricted local executor
    
    Adds basic safety checks:
    - Blocks dangerous imports
    - Validates code for obvious security issues
    
    Still INSECURE - only for development
    """
    
    DANGEROUS_IMPORTS = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'eval', 'exec', 'compile', '__import__', 'open', 'file',
        'input', 'raw_input', 'execfile'
    }
    
    DANGEROUS_KEYWORDS = [
        '__import__', 'eval(', 'exec(', 'compile(',
        'os.system', 'subprocess.', 'socket.', 'open('
    ]
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        """Initialize restricted local executor"""
        super().__init__(config)
        logger.info("RestrictedLocalExecutor initialized - Some safety checks enabled")
    
    async def execute(
        self,
        student_code: str,
        test_code: str,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """
        Execute with basic safety checks
        
        Args:
            student_code: Student's submitted code
            test_code: Test/grading code
            config_override: Optional configuration override
            
        Returns:
            ExecutionResult with execution details
        """
        # Validate student code for obvious security issues
        validation_error = self._validate_code(student_code)
        if validation_error:
            return ExecutionResult(
                success=False,
                error_message=validation_error,
                feedback=f"Code validation failed: {validation_error}"
            )
        
        # Execute with parent's logic
        return await super().execute(student_code, test_code, config_override)
    
    def _validate_code(self, code: str) -> Optional[str]:
        """
        Validate code for obvious security issues
        
        Args:
            code: Code to validate
            
        Returns:
            Error message if validation fails, None otherwise
        """
        # Check for dangerous keywords
        code_lower = code.lower()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword.lower() in code_lower:
                return f"Forbidden operation detected: {keyword}"
        
        # Check imports (basic check)
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Extract module name
                parts = line.split()
                if len(parts) >= 2:
                    module = parts[1].split('.')[0]
                    if module in self.DANGEROUS_IMPORTS:
                        return f"Forbidden import: {module}"
        
        return None
