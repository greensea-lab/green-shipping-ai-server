# GitHub 사용자 정보 확인 (Windows PowerShell)
Write-Host "🔍 GitHub 사용자 정보 확인" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

Write-Host "📋 현재 Git 설정:" -ForegroundColor Yellow
Write-Host "Name: $(git config --global user.name)" -ForegroundColor Cyan
Write-Host "Email: $(git config --global user.email)" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 GitHub 프로필 확인 방법:" -ForegroundColor Yellow
Write-Host "1. GitHub.com에 로그인" -ForegroundColor White
Write-Host "2. 우측 상단 프로필 아이콘 클릭" -ForegroundColor White
Write-Host "3. 프로필 페이지에서 'Name' 필드 확인" -ForegroundColor White
Write-Host "4. 또는 Settings → Account → Name 확인" -ForegroundColor White
Write-Host ""

Write-Host "🔧 Git 사용자명 설정:" -ForegroundColor Yellow
Write-Host "git config --global user.name 'Your GitHub Profile Name'" -ForegroundColor White
Write-Host "git config --global user.email 'your.email@example.com'" -ForegroundColor White
Write-Host ""

Write-Host "💡 예시:" -ForegroundColor Yellow
Write-Host "git config --global user.name 'gildong-hong'" -ForegroundColor White
Write-Host "git config --global user.email 'gildong-hong@gmail.com'" -ForegroundColor White 