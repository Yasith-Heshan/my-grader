"""
Abstract interface for code execution engines
Allows pluggable executors (Docker, local, cloud-based, etc.)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class ExecutionLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"


@dataclass
class ExecutionConfig:
    """Configuration for code execution"""
    language: ExecutionLanguage = ExecutionLanguage.PYTHON
    timeout: int = 10  # seconds
    memory_limit: str = "256m"  # Docker format: "256m", "1g"
    cpu_quota: int = 50000  # 50% of one core (100000 = 100%)
    network_disabled: bool = True
    read_only_rootfs: bool = True
    allowed_imports: Optional[List[str]] = None  # Whitelist of allowed imports
    max_output_size: int = 10240  # Maximum output in bytes (10KB)
    working_dir: str = "/sandbox"
    docker_image: Optional[str] = None  # Custom Docker image
    
    def __post_init__(self):
        """Validate configuration"""
        if self.timeout <= 0 or self.timeout > 300:
            raise ValueError("Timeout must be between 1 and 300 seconds")
        if self.cpu_quota <= 0 or self.cpu_quota > 400000:
            raise ValueError("CPU quota must be between 1 and 400000 (4 cores)")


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0  # seconds
    timeout_occurred: bool = False
    memory_used: Optional[int] = None  # bytes
    error_message: Optional[str] = None
    
    # Grading specific fields
    passed: bool = False
    score: float = 0.0
    max_score: float = 0.0
    feedback: str = ""
    test_results: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "success": self.success,
            "passed": self.passed,
            "score": self.score,
            "max_score": self.max_score,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "timeout_occurred": self.timeout_occurred,
            "memory_used": self.memory_used,
            "error_message": self.error_message,
            "feedback": self.feedback,
            "test_results": self.test_results
        }


class CodeExecutor(ABC):
    """Abstract base class for code executors"""
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        """
        Initialize executor with configuration
        
        Args:
            config: Execution configuration (uses defaults if None)
        """
        self.config = config or ExecutionConfig()
    
    @abstractmethod
    async def execute(
        self,
        student_code: str,
        test_code: str,
        config_override: Optional[ExecutionConfig] = None
    ) -> ExecutionResult:
        """
        Execute student code against test code
        
        Args:
            student_code: Student's submitted code
            test_code: Test/grading code to validate submission
            config_override: Optional configuration override for this execution
            
        Returns:
            ExecutionResult with output and grading information
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if executor is healthy and ready
        
        Returns:
            True if executor is ready, False otherwise
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Clean up any resources held by executor"""
        pass
    
    def get_config(self) -> ExecutionConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, config: ExecutionConfig):
        """Update executor configuration"""
        self.config = config
