# PHASE 5 - Complete Verification Suite

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "PHASE 5 COMPLETE VERIFICATION SUITE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Check if backend is running
Write-Host "`n[CHECK] Verifying backend is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/models" -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is running" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Backend not running!" -ForegroundColor Red
    Write-Host "   Please start backend first:" -ForegroundColor Yellow
    Write-Host "   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload" -ForegroundColor Gray
    exit 1
}

# Test 1: FK Constraints
Write-Host "`n[1/4] Checking FK Constraints..." -ForegroundColor Yellow
.\venv\Scripts\python.exe check_fk_constraints.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ FK constraint check failed" -ForegroundColor Red
    exit 1
}

# Test 2: Complete HTTP Test Suite
Write-Host "`n[2/4] Running Complete HTTP Test Suite..." -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
.\venv\Scripts\python.exe test_http_rag_complete.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ HTTP tests FAILED" -ForegroundColor Red
    Write-Host "See output above for details" -ForegroundColor Yellow
    exit 1
}

# Test 3: Direct Database Verification
Write-Host "`n[3/4] Direct Database Verification..." -ForegroundColor Yellow
.\venv\Scripts\python.exe verify_token_usage_kb_id.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Database verification failed" -ForegroundColor Red
    exit 1
}

# Test 4: Summary
Write-Host "`n[4/4] Verification Summary" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ FK CONSTRAINTS: CORRECT" -ForegroundColor Green
Write-Host "✅ HTTP TESTS: ALL 15 PASSED" -ForegroundColor Green
Write-Host "✅ DATABASE: TOKEN_USAGE KB_ID STORED CORRECTLY" -ForegroundColor Green
Write-Host "✅ ANALYTICS API: KB_ID IN RESPONSE" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green

Write-Host "`n🎉 PHASE 5 BACKEND COMPLETE!" -ForegroundColor Cyan
Write-Host "Ready for frontend implementation." -ForegroundColor Green
