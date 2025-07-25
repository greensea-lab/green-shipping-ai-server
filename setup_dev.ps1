# Green Shipping AI Server - Development Environment Setup (Windows)
# 이 스크립트는 Windows에서 개발 환경을 자동으로 설정합니다.

param(
    [switch]$SkipPythonCheck
)

# 스크립트 실행 정책 확인
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Host "❌ PowerShell 5.0 이상이 필요합니다." -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Green Shipping AI Server 개발 환경 설정을 시작합니다..." -ForegroundColor Green

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

# 1. Python 확인
if (-not $SkipPythonCheck) {
    Write-Step "Python 설치를 확인합니다..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python이 설치되어 있습니다: $pythonVersion"
        } else {
            throw "Python을 찾을 수 없습니다."
        }
    } catch {
        Write-Error "Python이 설치되지 않았습니다."
        Write-Host "Python을 설치해주세요: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "설치 시 'Add Python to PATH'를 반드시 체크해주세요." -ForegroundColor Yellow
        exit 1
    }
}

# 2. 가상환경 생성
Write-Step "Python 가상환경을 설정합니다..."

if (-not (Test-Path "venv")) {
    Write-Host "가상환경을 생성합니다..."
    python -m venv venv
    Write-Success "가상환경이 생성되었습니다."
} else {
    Write-Success "가상환경이 이미 존재합니다."
}

# 3. 가상환경 활성화
Write-Step "가상환경을 활성화합니다..."
& "venv\Scripts\Activate.ps1"
Write-Success "가상환경이 활성화되었습니다."

# 4. pip 업그레이드
Write-Step "pip를 최신 버전으로 업그레이드합니다..."
python -m pip install --upgrade pip

# 5. 의존성 설치
Write-Step "필요한 패키지들을 설치합니다..."
pip install -r requirements.txt
Write-Success "모든 패키지가 설치되었습니다."

# 6. 환경 변수 파일 확인
Write-Step "환경 변수 파일을 확인합니다..."
if (-not (Test-Path ".env")) {
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Warning ".env 파일이 생성되었습니다. 데이터베이스 설정을 확인해주세요."
    } else {
        Write-Error "env.example 파일을 찾을 수 없습니다."
        exit 1
    }
} else {
    Write-Success ".env 파일이 이미 존재합니다."
}

# 7. IDE 설정 파일 생성
Write-Step "IDE 설정 파일을 생성합니다..."

# VS Code 설정
if (-not (Test-Path ".vscode")) {
    New-Item -ItemType Directory -Path ".vscode" | Out-Null
}

$vscodeSettings = @{
    "python.defaultInterpreterPath" = "./venv/Scripts/python.exe"
    "python.terminal.activateEnvironment" = $true
    "python.linting.enabled" = $true
    "python.linting.pylintEnabled" = $true
    "python.formatting.provider" = "black"
    "python.analysis.autoImportCompletions" = $true
    "files.exclude" = @{
        "**/__pycache__" = $true
        "**/*.pyc" = $true
        "venv" = $false
    }
} | ConvertTo-Json -Depth 3

$vscodeSettings | Out-File -FilePath ".vscode\settings.json" -Encoding UTF8

# VS Code launch.json
$launchConfig = @{
    version = "0.2.0"
    configurations = @(
        @{
            name = "FastAPI"
            type = "python"
            request = "launch"
            module = "uvicorn"
            args = @("app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000")
            console = "integratedTerminal"
            python = "./venv/Scripts/python.exe"
            env = @{
                PYTHONPATH = "`${workspaceFolder}"
            }
        }
    )
} | ConvertTo-Json -Depth 3

$launchConfig | Out-File -FilePath ".vscode\launch.json" -Encoding UTF8

Write-Success "VS Code 설정이 완료되었습니다."

# 8. 개발용 스크립트 생성
Write-Step "개발용 스크립트를 생성합니다..."

$devScript = @"
# Green Shipping AI Server 개발 서버 실행 스크립트

Write-Host "🚀 Green Shipping AI Server 개발 서버를 시작합니다..." -ForegroundColor Green

# 가상환경 활성화
& "venv\Scripts\Activate.ps1"

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@

$devScript | Out-File -FilePath "dev.ps1" -Encoding UTF8

$testScript = @"
# API 테스트 스크립트

Write-Host "🧪 API 테스트를 실행합니다..." -ForegroundColor Blue

# 서버가 실행 중인지 확인
try {
    `$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ 서버가 실행 중입니다." -ForegroundColor Green
    Write-Host "📋 사용 가능한 API 엔드포인트:" -ForegroundColor Cyan
    Write-Host "   - 메인 페이지: http://localhost:8000" -ForegroundColor White
    Write-Host "   - API 문서: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   - 헬스 체크: http://localhost:8000/health" -ForegroundColor White
    Write-Host "   - 사용자 API: http://localhost:8000/api/v1/users/" -ForegroundColor White
} catch {
    Write-Host "❌ 서버가 실행되지 않았습니다. 먼저 .\dev.ps1로 서버를 시작해주세요." -ForegroundColor Red
}
"@

$testScript | Out-File -FilePath "test_api.ps1" -Encoding UTF8

Write-Success "개발용 스크립트가 생성되었습니다."

# 9. 완료 메시지
Write-Host ""
Write-Host "🎉 개발 환경 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 다음 단계:" -ForegroundColor Cyan
Write-Host "1. 데이터베이스 설정:" -ForegroundColor White
Write-Host "   - MySQL 서버 시작" -ForegroundColor White
Write-Host "   - 데이터베이스 생성: CREATE DATABASE green_shipping_db;" -ForegroundColor White
Write-Host ""
Write-Host "2. 서버 실행:" -ForegroundColor White
Write-Host "   .\dev.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. API 테스트:" -ForegroundColor White
Write-Host "   .\test_api.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. IDE에서 프로젝트 열기:" -ForegroundColor White
Write-Host "   - VS Code: code ." -ForegroundColor Yellow
Write-Host "   - PyCharm: 프로젝트 폴더 열기" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 자세한 내용은 README.md를 참고하세요." -ForegroundColor Cyan
Write-Host "" 