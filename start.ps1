# Discord Custom TTS Bot Launcher
# PowerShell script with better error handling

Write-Host "=== Discord Custom TTS Bot ===" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create .env file with required tokens" -ForegroundColor Yellow
}

# Kill existing bot processes
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" }
if ($processes) {
    Write-Host "Stopping existing bot processes..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Start bot
Write-Host "Starting bot..." -ForegroundColor Green
Write-Host ""

try {
    & "venv\Scripts\python.exe" bot.py
} catch {
    Write-Host "Error: Failed to start bot" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Read-Host "Press Enter to exit"
