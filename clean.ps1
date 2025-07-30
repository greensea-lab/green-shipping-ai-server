# Green Shipping AI Server - Windows PowerShell Clean Script
# Windows 환경에서 가상환경을 삭제하는 스크립트

Write-Host "🧹 Removing virtual environment..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Remove-Item -Recurse -Force "venv"
    Write-Host "✅ Virtual environment removed." -ForegroundColor Green
}
else {
    Write-Host "ℹ️ Virtual environment does not exist." -ForegroundColor Cyan
} 