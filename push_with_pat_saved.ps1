# GitHub PAT Push (저장된 토큰 사용) - Windows PowerShell
Write-Host "🔐 GitHub PAT Push (저장된 토큰 사용)" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# .env 파일 확인
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env 파일이 없습니다. 먼저 'make setup'을 실행해주세요." -ForegroundColor Red
    exit 1
}

# PAT 로드
$envContent = Get-Content ".env"
$GITHUB_PAT = ($envContent | Where-Object { $_ -match "GITHUB_PAT=" }) -replace "GITHUB_PAT=", ""

if (-not $GITHUB_PAT) {
    Write-Host "❌ PAT가 설정되지 않았습니다. 먼저 다음 명령어로 설정해주세요:" -ForegroundColor Red
    Write-Host "   .\setup_github_pat.ps1" -ForegroundColor White
    exit 1
}

# 원격 저장소 URL 업데이트
git remote set-url origin "https://${GITHUB_PAT}@github.com/greensea-lab/green-shipping-ai-server.git"

# 변경사항 확인
Write-Host "📋 Current changes:" -ForegroundColor Yellow
git status

# 커밋 메시지 입력
$COMMIT_MSG = Read-Host "Enter commit message"

# 커밋 및 Push
git add .
git commit -m "$COMMIT_MSG"
git push origin main

Write-Host "✅ Push completed successfully!" -ForegroundColor Green 