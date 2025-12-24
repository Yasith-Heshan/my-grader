# Build Docker images for code execution sandbox
# Windows PowerShell version

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DOCKER_DIR = $SCRIPT_DIR

Write-Host "Building Docker images for grading sandbox..." -ForegroundColor Cyan
Write-Host "=============================================="

# Build Python sandbox
Write-Host ""
Write-Host "Building Python 3.11 sandbox..." -ForegroundColor Yellow
Set-Location "$DOCKER_DIR\python"
docker build -t grader-python-sandbox:latest .

# Verify build
Write-Host ""
Write-Host "Verifying Python sandbox..." -ForegroundColor Yellow
docker run --rm grader-python-sandbox:latest python --version

Write-Host ""
Write-Host "=============================================="
Write-Host "✓ All images built successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Images created:"
docker images | Select-String "grader-python-sandbox"

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Set DOCKER_ENABLED=true in your environment"
Write-Host "2. Test the executor: pytest backend/tests/test_docker_executor.py"
Write-Host "3. Start the backend server with Docker execution enabled"
