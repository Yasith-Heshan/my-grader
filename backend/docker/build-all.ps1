# Build all Docker image variants
# Usage: .\build-all.ps1

$ErrorActionPreference = "Stop"

Write-Host "`n=== Building Docker Images ===" -ForegroundColor Cyan

# Build base image first
Write-Host "`nBuilding base image..." -ForegroundColor Yellow
Set-Location base
docker build -t grader-python-base:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build base image" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Build numpy variant
Write-Host "`nBuilding numpy image..." -ForegroundColor Yellow
Set-Location numpy
docker build -t grader-python-numpy:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build numpy image" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Build datascience variant
Write-Host "`nBuilding datascience image..." -ForegroundColor Yellow
Set-Location datascience
docker build -t grader-python-datascience:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build datascience image" -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host "`n=== Build Complete ===" -ForegroundColor Green
Write-Host "`nAvailable images:" -ForegroundColor Cyan
docker images | Select-String "grader-python"
