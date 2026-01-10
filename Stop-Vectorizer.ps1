# Stop-Vectorizer.ps1
# Clean shutdown for Vector Converter

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $scriptDir "server.pid"

Write-Host ""
Write-Host "  Stopping Vector Converter..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path $pidFile) {
    $pid = Get-Content $pidFile -ErrorAction SilentlyContinue

    if ($pid) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue

        if ($process) {
            # Stop the process and any child processes
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue

            # Also kill any python processes on port 5000 (in case of debug mode spawning children)
            $portProcesses = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty OwningProcess -Unique

            foreach ($p in $portProcesses) {
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            }

            Write-Host "Server stopped (PID: $pid)" -ForegroundColor Green
        } else {
            Write-Host "Server was not running (stale PID file)" -ForegroundColor Yellow
        }
    }

    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
} else {
    # Try to find and kill any python process on port 5000
    $portProcesses = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    if ($portProcesses) {
        foreach ($p in $portProcesses) {
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
        Write-Host "Stopped processes on port 5000" -ForegroundColor Green
    } else {
        Write-Host "No server found running" -ForegroundColor Yellow
    }
}

Write-Host ""
