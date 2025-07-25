# Green Shipping AI Server - 의존성 설치 스크립트 (Windows)
# requirements.txt에 추가된 패키지들을 자동으로 설치합니다.

Write-Host "📦 Green Shipping AI Server 의존성 설치를 시작합니다..." -ForegroundColor Green

# 함수 정의
function Write-Step {
    param([string]$Message)
    Write-Host "📋 $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# 1. 가상환경 확인
Write-Step "가상환경을 확인합니다..."

if (-not (Test-Path "venv")) {
    Write-Error "가상환경이 존재하지 않습니다."
    Write-Host "다음 명령어로 가상환경을 생성해주세요:" -ForegroundColor Yellow
    Write-Host "  .\setup_dev.ps1" -ForegroundColor Cyan
    exit 1
}

# 2. 가상환경 활성화
Write-Step "가상환경을 활성화합니다..."
& "venv\Scripts\Activate.ps1"
Write-Success "가상환경이 활성화되었습니다."

# 3. requirements.txt 확인
Write-Step "requirements.txt 파일을 확인합니다..."

if (-not (Test-Path "requirements.txt")) {
    Write-Error "requirements.txt 파일이 존재하지 않습니다."
    exit 1
}

# 4. 현재 설치된 패키지 백업
Write-Step "현재 설치된 패키지를 백업합니다..."
pip freeze > requirements_backup.txt
Write-Success "백업이 완료되었습니다: requirements_backup.txt"

# 5. 새로운 패키지 설치
Write-Step "requirements.txt의 패키지들을 설치합니다..."
pip install -r requirements.txt

# 6. 설치 결과 확인
Write-Step "설치 결과를 확인합니다..."
Write-Host ""
Write-Host "📊 설치된 패키지 목록:" -ForegroundColor Cyan
pip list

Write-Host ""
Write-Success "의존성 설치가 완료되었습니다!"
Write-Host ""
Write-Host "📋 다음 단계:" -ForegroundColor Yellow
Write-Host "1. 서버 실행: .\dev.ps1" -ForegroundColor White
Write-Host "2. API 테스트: .\test_api.ps1" -ForegroundColor White
Write-Host ""
Write-Host "💡 문제가 발생하면 다음 명령어로 백업에서 복원할 수 있습니다:" -ForegroundColor Gray
Write-Host "  pip install -r requirements_backup.txt" -ForegroundColor Cyan 