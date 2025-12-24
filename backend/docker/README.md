# Docker-based Secure Code Execution

This directory contains Docker configurations for secure, isolated code execution.

## Overview

The grading system uses Docker containers to execute student code in a secure, isolated environment. This prevents malicious code from accessing the host system, network, or other resources.

## Directory Structure

```
docker/
├── python/
│   ├── Dockerfile          # Python 3.11 sandbox image
│   └── requirements.txt    # Allowed Python packages
├── javascript/             # Future: Node.js sandbox
└── README.md              # This file
```

## Security Features

### Container Security
- **Non-root user**: Code runs as user `sandbox` (UID 1000)
- **Read-only filesystem**: Root filesystem is read-only
- **No network access**: Network is disabled by default
- **Limited capabilities**: All Linux capabilities dropped
- **Resource limits**: CPU, memory, and process limits enforced
- **Minimal image**: Alpine-based for reduced attack surface
- **No package manager**: pip/setuptools removed after build

### Runtime Security
- **Process isolation**: Each execution in separate container
- **Automatic cleanup**: Containers destroyed after execution
- **Timeout enforcement**: Hard timeout on code execution
- **Output limits**: Stdout/stderr truncated to prevent DoS
- **Temporary storage**: Only /tmp writable, limited to 10MB

## Building Images

### Python Sandbox

```bash
# From backend directory
cd docker/python
docker build -t grader-python-sandbox:latest .
```

### Verify Build

```bash
docker run --rm grader-python-sandbox:latest python --version
# Should output: Python 3.11.x
```

## Usage

The Docker executor is used automatically by the grading system when Docker is available and enabled.

### Configuration

Set environment variables in `.env` or system environment:

```bash
# Enable Docker execution
DOCKER_ENABLED=true

# Docker host (auto-detected on most systems)
# Linux/Mac: unix:///var/run/docker.sock
# Windows: npipe:////./pipe/docker_engine
DOCKER_HOST=unix:///var/run/docker.sock

# Fallback to local execution if Docker unavailable (dev only)
FALLBACK_TO_LOCAL=true

# Resource limits
DEFAULT_TIMEOUT=10           # seconds
DEFAULT_MEMORY_LIMIT=256m    # 256 MB
DEFAULT_CPU_QUOTA=50000      # 50% of one core
```

### Testing

Test the Docker executor:

```python
from utils.docker_executor import DockerExecutor
from utils.executor_interface import ExecutionConfig

# Create executor
executor = DockerExecutor()

# Test code
student_code = """
def add(a, b):
    return a + b

result = add(2, 3)
"""

test_code = """
# Test the function
passed = result == 5
score = 10.0 if passed else 0.0
max_score = 10.0
feedback = "Correct!" if passed else "Incorrect"
"""

# Execute
result = await executor.execute(student_code, test_code)
print(f"Score: {result.score}/{result.max_score}")
```

## Adding New Languages

To add support for a new language (e.g., JavaScript):

1. Create directory: `docker/javascript/`
2. Create `Dockerfile` with security hardening
3. Create `requirements.txt` or equivalent
4. Update `config/executor_config.py` with image name
5. Build and test the image

### JavaScript Example

```dockerfile
FROM node:18-alpine

RUN adduser -D -u 1000 sandbox
WORKDIR /sandbox
USER sandbox

ENV NODE_ENV=production
CMD ["node", "--version"]
```

## Troubleshooting

### Docker Not Found

**Issue**: "Docker client not available"

**Solutions**:
- Ensure Docker Desktop is running (Windows/Mac)
- Verify Docker service is running: `systemctl status docker` (Linux)
- Check Docker socket permissions: `/var/run/docker.sock`

### Permission Denied

**Issue**: "Permission denied" when accessing Docker

**Solutions**:
- Add user to docker group: `sudo usermod -aG docker $USER`
- Log out and back in
- Or run with sudo (not recommended)

### Image Not Found

**Issue**: "Image 'grader-python-sandbox:latest' not found"

**Solution**:
```bash
cd backend/docker/python
docker build -t grader-python-sandbox:latest .
```

### Windows Named Pipe Issues

**Issue**: Cannot connect on Windows

**Solutions**:
- Ensure Docker Desktop is running
- Try: `DOCKER_HOST=tcp://localhost:2375`
- Enable "Expose daemon on tcp://localhost:2375" in Docker Desktop settings

### Container Timeout

**Issue**: Containers keep timing out

**Solutions**:
- Increase `DEFAULT_TIMEOUT` in configuration
- Check CPU quota isn't too restrictive
- Verify host system has sufficient resources

## Monitoring

### View Running Containers

```bash
docker ps --filter "label=grader=true"
```

### View Container Logs

```bash
docker logs <container_id>
```

### Clean Up

```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -f
```

## Best Practices

1. **Keep images minimal**: Only include necessary packages
2. **Regular updates**: Rebuild images regularly for security patches
3. **Test security**: Attempt to escape sandbox, access files, network
4. **Monitor resources**: Track container CPU/memory usage
5. **Rotate images**: Use versioned tags, not just `:latest`
6. **Log execution**: Enable execution logging for debugging
7. **Rate limiting**: Implement rate limits on execution API

## Security Considerations

### What This Protects Against
- File system access outside sandbox
- Network access to external services
- Process fork bombs
- Memory exhaustion
- CPU hogging
- Privilege escalation

### What This Doesn't Protect Against
- Side-channel attacks (e.g., timing attacks)
- Docker daemon vulnerabilities
- Host kernel vulnerabilities
- Algorithmic complexity attacks (use timeouts)

### Production Recommendations
1. **Never use local executor** in production
2. **Keep Docker updated** to latest stable version
3. **Use AppArmor/SELinux** for additional kernel-level security
4. **Monitor containers** for unusual behavior
5. **Implement rate limiting** on grading endpoints
6. **Log all executions** for audit trail
7. **Regular security audits** of Docker configurations

## Performance

Expected execution times:
- Container creation: 100-200ms
- Code execution: Varies (typically <1s)
- Container cleanup: 50-100ms
- **Total overhead**: ~200-400ms per execution

For high-volume grading:
- Use container pooling (future enhancement)
- Increase `MAX_CONCURRENT_CONTAINERS`
- Consider distributed execution across multiple Docker hosts

## References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
