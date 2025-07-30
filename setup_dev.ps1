# Green Shipping AI Server - Windows PowerShell Setup Script
# Windows 환경에서 개발 환경을 설정하는 스크립트

Write-Host "🚀 개발 environment setup..." -ForegroundColor Green

# 가상환경 생성
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
# 가상환경 활성화
.\venv\Scripts\Activate.ps1

Write-Host "📚 Installing required packages..." -ForegroundColor Yellow
# pip 업그레이드
.\venv\Scripts\pip.exe install --upgrade pip

# 패키지 설치
.\venv\Scripts\pip.exe install -r requirements.txt

# .env 파일 생성
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Creating environment file..." -ForegroundColor Yellow
    if (Test-Path "env.local") {
        Copy-Item "env.local" ".env"
        Write-Host "✅ .env file created with local environment settings." -ForegroundColor Green
    }
    elseif (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "⚠️ .env file created. Please check environment-specific settings." -ForegroundColor Yellow
    }
}

Write-Host "✅ Development environment setup completed!" -ForegroundColor Green 