# Green Shipping AI Server - 환경별 설정 확인 스크립트 (Windows)
# 현재 환경 설정과 사용 가능한 환경들을 확인합니다.

Write-Host "🔍 Green Shipping AI Server 환경별 설정 확인" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Blue

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

# 1. 현재 환경 확인
Write-Step "현재 환경 설정 확인"

if (Test-Path ".env") {
    Write-Success ".env 파일이 존재합니다."
    
    # DATABASE_URL 확인
    $envContent = Get-Content ".env"
    $dbUrlLine = $envContent | Where-Object { $_ -match "DATABASE_URL" }
    
    if ($dbUrlLine) {
        $dbUrl = $dbUrlLine.Split('=')[1]
        if ($dbUrl -like "*sqlite*") {
            Write-Success "현재 설정: SQLite (로컬 환경)"
        } elseif ($dbUrl -like "*mysql*") {
            $debugLine = $envContent | Where-Object { $_ -match "DEBUG=True" }
            if ($debugLine) {
                Write-Success "현재 설정: MySQL (개발 환경)"
            } else {
                Write-Warning "현재 설정: MySQL (프로덕션 환경)"
            }
        } else {
            Write-Warning "현재 설정: 알 수 없는 데이터베이스"
        }
    } else {
        Write-Error "DATABASE_URL이 설정되지 않았습니다."
    }
} else {
    Write-Error ".env 파일이 없습니다."
}

Write-Host ""

# 2. 환경별 설정 파일 확인
Write-Step "환경별 설정 파일 확인"

# 로컬 환경
if (Test-Path "env.local") {
    Write-Success "env.local (로컬 환경) - 존재"
    $localContent = Get-Content "env.local"
    if ($localContent -match "sqlite") {
        Write-Success "  → SQLite 데이터베이스 사용"
    }
} else {
    Write-Error "env.local (로컬 환경) - 없음"
}

# 개발 환경
if (Test-Path "env.dev") {
    Write-Success "env.dev (개발 환경) - 존재"
    $devContent = Get-Content "env.dev"
    if ($devContent -match "mysql") {
        Write-Success "  → MySQL 데이터베이스 사용"
    }
} else {
    Write-Error "env.dev (개발 환경) - 없음"
}

# 프로덕션 환경
if (Test-Path "env.production") {
    Write-Success "env.production (프로덕션 환경) - 존재"
    $prodContent = Get-Content "env.production"
    if ($prodContent -match "mysql") {
        Write-Success "  → MySQL 데이터베이스 사용"
    }
} else {
    Write-Error "env.production (프로덕션 환경) - 없음"
}

Write-Host ""

# 3. 사용 가능한 명령어
Write-Step "사용 가능한 환경별 명령어"

Write-Host "📋 서버 실행:" -ForegroundColor Yellow
Write-Host "  make local  # 로컬 환경 (SQLite)" -ForegroundColor White
Write-Host "  make dev        # 개발 환경 (원격 MySQL)" -ForegroundColor White
Write-Host "  make prod       # 프로덕션 환경 (원격 MySQL)" -ForegroundColor White
Write-Host ""

Write-Host "📋 마이그레이션:" -ForegroundColor Yellow
Write-Host "  make migrate    # 로컬 마이그레이션 (SQLite)" -ForegroundColor White
Write-Host "  make migrate-dev # 개발 환경 마이그레이션 (MySQL)" -ForegroundColor White
Write-Host "  make migrate-prod # 프로덕션 마이그레이션 (보안상 제한)" -ForegroundColor White
Write-Host ""

# 4. 환경 전환 방법
Write-Step "환경 전환 방법"

Write-Host "💡 환경을 변경하려면:" -ForegroundColor Yellow
Write-Host "  1. 원하는 환경 설정 파일을 .env로 복사" -ForegroundColor White
Write-Host "  2. 해당 환경의 서버 실행 명령어 사용" -ForegroundColor White
Write-Host ""
Write-Host "예시:" -ForegroundColor Yellow
Write-Host "  Copy-Item env.dev .env; make dev" -ForegroundColor White
Write-Host "  Copy-Item env.local .env; make local" -ForegroundColor White
Write-Host ""

# 5. 현재 상태 요약
Write-Step "현재 상태 요약"

if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    if ($envContent -match "sqlite") {
        Write-Host "🎯 현재 환경: 로컬 (SQLite)" -ForegroundColor Green
        Write-Host "💡 권장 명령어: make local" -ForegroundColor Cyan
    } elseif ($envContent -match "mysql") {
        if ($envContent -match "DEBUG=True") {
            Write-Host "🎯 현재 환경: 개발 (MySQL)" -ForegroundColor Green
            Write-Host "💡 권장 명령어: make dev" -ForegroundColor Cyan
        } else {
            Write-Host "🎯 현재 환경: 프로덕션 (MySQL)" -ForegroundColor Green
            Write-Host "💡 권장 명령어: make prod" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "🎯 현재 환경: 설정되지 않음" -ForegroundColor Yellow
    Write-Host "💡 권장 명령어: make setup" -ForegroundColor Cyan
}

Write-Host ""
Write-Success "환경 확인이 완료되었습니다!" 