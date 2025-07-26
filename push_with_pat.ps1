# GitHub PAT Push Script
Write-Host "🔐 GitHub PAT Push Script" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

# PAT 입력 받기
$PAT = Read-Host "Enter your GitHub Personal Access Token" -AsSecureString
$PAT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PAT))

# 원격 저장소 URL 업데이트
git remote set-url origin "https://${PAT}@github.com/greensea-lab/green-shipping-ai-server.git"

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