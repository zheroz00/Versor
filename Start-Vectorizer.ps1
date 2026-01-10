# Start-Vectorizer.ps1
# One-click launcher for Vector Converter

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $scriptDir "server.pid"
$port = 5000
$url = "http://localhost:$port"

# Check if already running
if (Test-Path $pidFile) {
    $existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
        Write-Host "Vector Converter is already running (PID: $existingPid)" -ForegroundColor Yellow
        Write-Host "Opening browser..." -ForegroundColor Cyan
        Start-Process $url
        exit 0
    }
}

Write-Host ""
Write-Host "  Vector Converter" -ForegroundColor Cyan
Write-Host "  ================" -ForegroundColor Cyan
Write-Host ""

# Start the Flask server in background
$env:FLASK_APP = "app.py"
$process = Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $scriptDir -PassThru -WindowStyle Hidden

# Save PID for clean shutdown
$process.Id | Out-File $pidFile -Force

Write-Host "Server started (PID: $($process.Id))" -ForegroundColor Green
Write-Host "URL: $url" -ForegroundColor Green
Write-Host ""

# Wait a moment for server to start
Start-Sleep -Seconds 2

# Open browser
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Process $url

Write-Host ""
Write-Host "To stop the server, run: .\Stop-Vectorizer.ps1" -ForegroundColor Yellow
Write-Host "Or double-click Stop-Vectorizer.bat" -ForegroundColor Yellow
