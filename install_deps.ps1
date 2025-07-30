# Green Shipping AI Server - Windows PowerShell Package Installation Script
# Windows 환경에서 패키지를 설치하는 스크립트

Write-Host "📚 Installing packages..." -ForegroundColor Green

# 가상환경 확인
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment does not exist. Please run '.\setup_dev.ps1' first." -ForegroundColor Red
    exit 1
}

# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# pip 업그레이드
.\venv\Scripts\pip.exe install --upgrade pip

# 패키지 설치
.\venv\Scripts\pip.exe install -r requirements.txt

Write-Host "✅ Package installation completed!" -ForegroundColor Green 