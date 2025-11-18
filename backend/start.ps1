# Quick Start Script for Windows PowerShell

Write-Host "🚀 Starting Python Notebook Grading System..." -ForegroundColor Green
Write-Host ""

# Check if MongoDB is running
Write-Host "📊 Checking MongoDB connection..." -ForegroundColor Yellow
try {
    $mongoTest = mongosh --eval "db.version()" --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MongoDB is running" -ForegroundColor Green
    } else {
        Write-Host "❌ MongoDB is not running" -ForegroundColor Red
        Write-Host "Please start MongoDB with: mongod --dbpath=C:\data\db" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ MongoDB not found or not running" -ForegroundColor Red
    Write-Host "Please ensure MongoDB is installed and running" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📦 Checking Python dependencies..." -ForegroundColor Yellow

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "🎯 Starting FastAPI server..." -ForegroundColor Green
Write-Host "📝 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📊 Alternative Docs: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python main.py
