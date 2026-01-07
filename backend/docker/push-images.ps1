# Push Docker images to Docker Hub
# Usage: .\push-images.ps1 <dockerhub-username>
# Example: .\push-images.ps1 yourusername

param(
    [Parameter(Mandatory=$true)]
    [string]$Username
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Pushing Docker Images to Docker Hub ===" -ForegroundColor Cyan
Write-Host "Username: $Username`n" -ForegroundColor Yellow

# Login check
Write-Host "Checking Docker Hub login..." -ForegroundColor Yellow
docker info | Select-String "Username" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Docker Hub first: docker login" -ForegroundColor Red
    exit 1
}

$variants = @("base", "numpy", "datascience")

foreach ($variant in $variants) {
    $localTag = "grader-python-$variant`:latest"
    $remoteTag = "$Username/grader-python-$variant`:latest"
    
    Write-Host "`nTagging $localTag as $remoteTag..." -ForegroundColor Yellow
    docker tag $localTag $remoteTag
    
    Write-Host "Pushing $remoteTag..." -ForegroundColor Yellow
    docker push $remoteTag
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to push $remoteTag" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n=== Push Complete ===" -ForegroundColor Green
Write-Host "`nImages pushed to Docker Hub:" -ForegroundColor Cyan
foreach ($variant in $variants) {
    Write-Host "  - $Username/grader-python-$variant`:latest" -ForegroundColor White
}
