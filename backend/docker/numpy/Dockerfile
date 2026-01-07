# Python NumPy Sandbox - Extends base with NumPy and Pandas
FROM grader-python-base:latest

USER root

# Copy requirements
COPY requirements.txt .

# Reinstall pip, install dependencies, then remove pip
RUN apk add --no-cache gcc musl-dev linux-headers && \
    python -m ensurepip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev linux-headers && \
    python -m pip uninstall -y pip setuptools

USER sandbox

LABEL description="Python sandbox with NumPy and Pandas"
