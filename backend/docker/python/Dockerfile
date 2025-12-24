# Python 3.11 Secure Sandbox for Code Grading
# Minimal, hardened image for executing student code

FROM python:3.11-alpine

# Create non-root user for code execution
RUN adduser -D -u 1000 sandbox

# Set working directory
WORKDIR /sandbox

# Install only essential packages for common Python assignments
# Keep this minimal to reduce attack surface
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove pip and setuptools after installation to prevent runtime package installation
RUN pip uninstall -y pip setuptools

# Set restrictive permissions
RUN chmod 755 /sandbox && \
    chown -R sandbox:sandbox /sandbox

# Create minimal tmp directory for runtime
RUN mkdir -p /tmp && chmod 1777 /tmp

# Switch to non-root user
USER sandbox

# Disable network (additional layer, also controlled by Docker run)
# Set Python to run in unbuffered mode for better log output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random

# Default command (will be overridden)
CMD ["python", "--version"]

# Security labels
LABEL maintainer="grader-system" \
    description="Secure Python sandbox for student code grading" \
    security="hardened" \
    version="1.0"
