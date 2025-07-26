# Green Shipping AI Server - 가상환경 활성화 스크립트 (Windows)
# IDE 터미널에서 이 스크립트를 실행하면 가상환경이 활성화됩니다.

Write-Host "🔧 Green Shipping AI Server 가상환경을 활성화합니다..." -ForegroundColor Blue

# 현재 디렉토리가 프로젝트 루트인지 확인
if (-not (Test-Path "requirements.txt") -or -not (Test-Path "app")) {
    Write-Host "❌ 현재 디렉토리가 Green Shipping AI Server 프로젝트가 아닙니다." -ForegroundColor Red
    Write-Host "프로젝트 루트 디렉토리로 이동해주세요." -ForegroundColor Yellow
    exit 1
}

# 가상환경이 존재하는지 확인
if (-not (Test-Path "venv")) {
    Write-Host "❌ 가상환경이 존재하지 않습니다." -ForegroundColor Red
    Write-Host "다음 명령어로 가상환경을 생성해주세요:" -ForegroundColor Yellow
    Write-Host "  .\setup_dev.ps1" -ForegroundColor Cyan
    exit 1
}

# 가상환경 활성화
& "venv\Scripts\Activate.ps1"

# 활성화 확인
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ 가상환경이 활성화되었습니다: $env:VIRTUAL_ENV" -ForegroundColor Green
    Write-Host "🐍 Python 경로: $(Get-Command python | Select-Object -ExpandProperty Source)" -ForegroundColor Cyan
    Write-Host "📦 pip 경로: $(Get-Command pip | Select-Object -ExpandProperty Source)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 사용 가능한 명령어:" -ForegroundColor Yellow
    Write-Host "  make local    # 로컬 개발 서버 실행 (SQLite)" -ForegroundColor White
    Write-Host "  make dev          # 개발 환경 서버 실행 (원격 MySQL)" -ForegroundColor White
    Write-Host "  make prod         # 프로덕션 환경 서버 실행 (원격 MySQL)" -ForegroundColor White
    Write-Host "  make test         # API 테스트" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 이 터미널을 닫으면 가상환경이 비활성화됩니다." -ForegroundColor Gray
} else {
    Write-Host "❌ 가상환경 활성화에 실패했습니다." -ForegroundColor Red
    exit 1
} 