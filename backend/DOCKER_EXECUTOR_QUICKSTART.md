# Docker Executor Utility - Quick Start Guide

## Overview

The Docker executor utility provides secure, isolated code execution for grading student submissions. This pluggable component can easily replace the current insecure `exec()` based grading system.

## Files Created

### Core Components
- `backend/utils/executor_interface.py` - Abstract interface for executors
- `backend/utils/docker_executor.py` - Docker-based secure executor
- `backend/utils/local_executor.py` - Local fallback executor (dev only)
- `backend/utils/executor_factory.py` - Factory for creating executors
- `backend/config/executor_config.py` - Configuration system

### Docker Configuration
- `backend/docker/python/Dockerfile` - Python sandbox image
- `backend/docker/python/requirements.txt` - Allowed packages
- `backend/docker/build.sh` - Build script (Linux/Mac)
- `backend/docker/build.ps1` - Build script (Windows)
- `backend/docker/README.md` - Comprehensive documentation

### Examples & Documentation
- `backend/utils/executor_examples.py` - Usage examples
- This file (QUICKSTART.md)

## Setup

### 1. Build Docker Image

**Windows (PowerShell):**
```powershell
cd backend/docker
./build.ps1
```

**Linux/Mac:**
```bash
cd backend/docker
chmod +x build.sh
./build.sh
```

### 2. Configure Environment

Create `.env` file in `backend/` directory:

```env
# Enable Docker execution
DOCKER_ENABLED=true

# Fallback to local execution if Docker unavailable (dev only)
FALLBACK_TO_LOCAL=true

# Resource limits
DEFAULT_TIMEOUT=10
DEFAULT_MEMORY_LIMIT=256m
DEFAULT_CPU_QUOTA=50000

# Security
NETWORK_DISABLED=true
READ_ONLY_ROOTFS=true
```

### 3. Install Python Dependencies

```bash
cd backend
pip install docker
```

## Basic Usage

### Simple Example

```python
from utils.executor_factory import ExecutorFactory

async def grade_code():
    # Create executor (automatically selects Docker or local)
    executor = await ExecutorFactory.create_executor()
    
    # Student's code
    student_code = """
def add(a, b):
    return a + b
result = add(2, 3)
"""
    
    # Test code
    test_code = """
passed = result == 5
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Correct!" if passed else "Incorrect"
"""
    
    # Execute securely in Docker
    result = await executor.execute(student_code, test_code)
    
    print(f"Score: {result.score}/{result.max_score}")
    print(f"Feedback: {result.feedback}")
    
    # Cleanup
    await executor.cleanup()
```

### With Custom Configuration

```python
from utils.executor_interface import ExecutionConfig, ExecutionLanguage
from utils.executor_factory import ExecutorFactory

async def grade_with_config():
    # Custom configuration
    config = ExecutionConfig(
        language=ExecutionLanguage.PYTHON,
        timeout=5,           # 5 second timeout
        memory_limit="128m", # 128 MB limit
        cpu_quota=25000,     # 25% CPU
        network_disabled=True
    )
    
    executor = await ExecutorFactory.create_executor(config)
    result = await executor.execute(student_code, test_code)
    await executor.cleanup()
```

## Integration with Grader Service

### Current Code (INSECURE)

```python
# backend/services/grader_service.py (line 34, 37)
namespace = {}
exec(submission_item.submitted_code, namespace)
exec(test_case.test_code, namespace)
```

### New Code (SECURE)

```python
from utils.executor_factory import ExecutorFactory

async def grade_single_cell(test_case, submission_item):
    """Grade using secure Docker execution"""
    
    # Create executor
    executor = await ExecutorFactory.create_executor()
    
    # Execute in isolated container
    result = await executor.execute(
        student_code=submission_item.submitted_code,
        test_code=test_case.test_code
    )
    
    # Cleanup
    await executor.cleanup()
    
    return {
        'passed': result.passed,
        'score': result.score,
        'max_score': result.max_score,
        'output': result.stdout,
        'feedback': result.feedback
    }
```

## Testing

### Run Examples

```bash
cd backend
python -m utils.executor_examples
```

### Validate Setup

```python
from utils.executor_factory import ExecutorFactory

async def validate():
    is_valid, issues = await ExecutorFactory.validate_setup()
    
    if is_valid:
        print("✓ Setup is valid!")
    else:
        for issue in issues:
            print(f"✗ {issue}")
```

## Development Mode

For development without Docker:

```env
DOCKER_ENABLED=false
FALLBACK_TO_LOCAL=true
```

This uses `RestrictedLocalExecutor` with basic safety checks (still insecure, dev only).

## Security Features

✅ **Process Isolation** - Each execution in separate container  
✅ **Resource Limits** - CPU, memory, and time constraints  
✅ **Network Isolation** - No external network access  
✅ **File System Protection** - Read-only root, limited /tmp  
✅ **No Privilege Escalation** - Non-root user, dropped capabilities  
✅ **Automatic Cleanup** - Containers destroyed after execution  
✅ **Cross-Platform** - Works on Windows, Linux, macOS  

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKER_ENABLED` | `true` | Enable Docker execution |
| `FALLBACK_TO_LOCAL` | `true` | Allow local fallback if Docker unavailable |
| `DEFAULT_TIMEOUT` | `10` | Execution timeout (seconds) |
| `DEFAULT_MEMORY_LIMIT` | `256m` | Memory limit per container |
| `DEFAULT_CPU_QUOTA` | `50000` | CPU quota (50% of one core) |
| `MAX_CONCURRENT_CONTAINERS` | `10` | Maximum concurrent executions |
| `NETWORK_DISABLED` | `true` | Disable network access |
| `READ_ONLY_ROOTFS` | `true` | Make root filesystem read-only |

## Troubleshooting

### Docker Not Found

```
Error: Docker client not available
```

**Solution**: Ensure Docker Desktop is running and accessible.

### Image Not Found

```
Error: Image 'grader-python-sandbox:latest' not found
```

**Solution**: Build the image:
```bash
cd backend/docker
./build.ps1  # Windows
./build.sh   # Linux/Mac
```

### Permission Denied (Linux)

```
Error: Permission denied accessing Docker
```

**Solution**: Add user to docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Windows Named Pipe Error

**Solution**: Enable "Expose daemon on tcp://localhost:2375" in Docker Desktop settings, then set:
```env
DOCKER_HOST=tcp://localhost:2375
```

## Next Steps

1. **Build Docker image** (see Setup section)
2. **Run examples** to verify setup
3. **Update grader_service.py** to use Docker executor
4. **Test with sample submissions**
5. **Deploy to production** (ensure `DOCKER_ENABLED=true`)

## API Reference

### ExecutorFactory

```python
# Create executor
executor = await ExecutorFactory.create_executor(config=None, force_docker=False, force_local=False)

# Get default executor
executor = await ExecutorFactory.get_default_executor()

# Validate setup
is_valid, issues = await ExecutorFactory.validate_setup()
```

### CodeExecutor

```python
# Execute code
result = await executor.execute(student_code, test_code, config_override=None)

# Health check
is_healthy = await executor.health_check()

# Cleanup
await executor.cleanup()
```

### ExecutionResult

```python
result.success         # bool: Execution succeeded
result.passed          # bool: Tests passed
result.score           # float: Points earned
result.max_score       # float: Maximum points
result.stdout          # str: Standard output
result.stderr          # str: Standard error
result.execution_time  # float: Time in seconds
result.timeout_occurred # bool: Execution timed out
result.feedback        # str: Feedback message
result.test_results    # list: Individual test results
```

## Production Checklist

- [ ] Docker images built and tested
- [ ] Configuration validated (`validate_setup()`)
- [ ] `DOCKER_ENABLED=true` in production
- [ ] `FALLBACK_TO_LOCAL=false` in production
- [ ] Resource limits configured appropriately
- [ ] Monitoring and logging enabled
- [ ] Rate limiting implemented on grading endpoints
- [ ] Security audit completed
- [ ] Backup executor strategy defined

## Support

For detailed documentation, see:
- `backend/docker/README.md` - Comprehensive Docker documentation
- `backend/utils/executor_examples.py` - Usage examples
- `backend/utils/executor_interface.py` - API documentation

For issues or questions, refer to the security considerations and troubleshooting sections in the documentation.
