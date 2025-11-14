# Armenian Rhyme Finder - Quick Start Script for Windows PowerShell

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Armenian Rhyme Finder - Quick Start" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.7+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import flask; import flask_cors" 2>&1 | Out-Null
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check if dictionary exists
Write-Host ""
Write-Host "Checking dictionary file..." -ForegroundColor Yellow
if (Test-Path "dictionary-hy-improved.jsonl") {
    $fileSize = (Get-Item "dictionary-hy-improved.jsonl").Length / 1MB
    Write-Host "✓ dictionary-hy-improved.jsonl found ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "✗ dictionary-hy-improved.jsonl not found in current directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the backend
Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Yellow
Write-Host ""

# Create a PowerShell job to run the backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    python backend.py
} -ArgumentList (Get-Location).Path

Start-Sleep -Seconds 2

# Check if backend started successfully
if ($backendJob.State -eq "Running") {
    Write-Host "✓ Backend started successfully on http://localhost:5000" -ForegroundColor Green
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Open your browser to the frontend:" -ForegroundColor White
    Write-Host "   file:///c:/Users/Nazani/Desktop/armenian-rhyme-app/index.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   OR serve with a local HTTP server:" -ForegroundColor White
    Write-Host "   python -m http.server 8000" -ForegroundColor Cyan
    Write-Host "   Then visit: http://localhost:8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. The backend will run until you close this window" -ForegroundColor White
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Wait for the backend job to complete
    $backendJob | Wait-Job
} else {
    Write-Host "✗ Failed to start backend" -ForegroundColor Red
    $backendJob | Receive-Job
    Read-Host "Press Enter to exit"
    exit 1
}
