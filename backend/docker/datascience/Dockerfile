# Python Data Science Sandbox - Full data science stack
FROM grader-python-base:latest

USER root

# Copy requirements
COPY requirements.txt .

# Install system dependencies, reinstall pip, install packages, cleanup
RUN apk add --no-cache \
    gcc musl-dev linux-headers \
    freetype-dev libpng-dev \
    openblas-dev gfortran && \
    python -m ensurepip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev gfortran && \
    python -m pip uninstall -y pip setuptools

USER sandbox

LABEL description="Python sandbox with full data science stack"
