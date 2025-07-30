# Green Shipping AI Server - Windows PowerShell Local Server Script
# Windows 환경에서 로컬 개발 서버를 실행하는 스크립트

Write-Host "🚀 Starting local development server (SQLite)..." -ForegroundColor Green

# 가상환경 확인
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment does not exist. Please run '.\setup_dev.ps1' first." -ForegroundColor Red
    exit 1
}

# 환경 파일 설정
if (Test-Path "env.local") {
    Copy-Item "env.local" ".env"
    Write-Host "✅ Using local environment settings." -ForegroundColor Green
}
else {
    Write-Host "⚠️ env.local file not found. Using default settings." -ForegroundColor Yellow
}

Write-Host "🔧 Starting server..." -ForegroundColor Yellow
Write-Host "💡 Press Ctrl+C to stop the server." -ForegroundColor Cyan
Write-Host "🌐 Server address: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# 가상환경 활성화 후 서버 실행
.\venv\Scripts\Activate.ps1
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 