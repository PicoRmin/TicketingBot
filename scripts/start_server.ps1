# Script to start FastAPI server
# Usage: .\scripts\start_server.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting Iranmehr Ticketing System..." -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}
else {
    Write-Host "Virtual environment not found. Using system Python." -ForegroundColor Yellow
}

# Check if port 8000 is already in use
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Port 8000 is already in use!" -ForegroundColor Red
    Write-Host "Please stop the existing server or use a different port." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting server on http://0.0.0.0:8000" -ForegroundColor Cyan
Write-Host "Logs will be written to logs/app.log" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}
catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
    exit 1
}
