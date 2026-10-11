# PHASE 5 - Restart Backend and Run Tests

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "PHASE 5 BACKEND RESTART AND TEST" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Stop existing backend
Write-Host "`n[1/4] Stopping existing backend processes..." -ForegroundColor Yellow
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*backend*" -or $_.Path -like "*uvicorn*" 
} | ForEach-Object {
    Write-Host "   Stopping process $($_.Id)..." -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# Start backend
Write-Host "`n[2/4] Starting backend server..." -ForegroundColor Yellow
$backend = Start-Process -FilePath ".\venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" `
    -WorkingDirectory (Get-Location) `
    -PassThru `
    -WindowStyle Normal

Write-Host "   Backend PID: $($backend.Id)" -ForegroundColor Green

# Wait for backend
Write-Host "`n[3/4] Waiting for backend to be ready..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/models" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Backend ready!" -ForegroundColor Green
            $ready = $true
            break
        }
    } catch {
        # Continue waiting
    }
    
    if ($i % 5 -eq 0 -and $i -gt 0) {
        Write-Host "   Still waiting... ($i s)" -ForegroundColor Gray
    }
    Start-Sleep -Seconds 1
}

if (-not $ready) {
    Write-Host "   ❌ Backend not ready after 30s" -ForegroundColor Red
    Write-Host "   Check backend window for errors" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "`n[4/4] Running complete test suite..." -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
.\venv\Scripts\python.exe test_http_rag_complete.py

Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "TESTING COMPLETE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "`nBackend is running in a separate window." -ForegroundColor Green
Write-Host "To stop: Get-Process -Id $($backend.Id) | Stop-Process" -ForegroundColor Gray
