#!/usr/bin/env bash
# Build Docker images for code execution sandbox

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR"

echo "Building Docker images for grading sandbox..."
echo "=============================================="

# Build Python sandbox
echo ""
echo "Building Python 3.11 sandbox..."
cd "$DOCKER_DIR/python"
docker build -t grader-python-sandbox:latest .

# Verify build
echo ""
echo "Verifying Python sandbox..."
docker run --rm grader-python-sandbox:latest python --version

echo ""
echo "=============================================="
echo "✓ All images built successfully!"
echo ""
echo "Images created:"
docker images | grep grader-python-sandbox

echo ""
echo "Next steps:"
echo "1. Set DOCKER_ENABLED=true in your environment"
echo "2. Test the executor: python -m pytest backend/tests/test_docker_executor.py"
echo "3. Start the backend server with Docker execution enabled"
