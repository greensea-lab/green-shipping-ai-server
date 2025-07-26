# GitHub PAT 초기 설정 (Windows PowerShell)
Write-Host "🔐 GitHub PAT 초기 설정" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# .env 파일 확인
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env 파일이 없습니다. 먼저 'make setup'을 실행해주세요." -ForegroundColor Red
    exit 1
}

# PAT 입력 받기
$PAT = Read-Host "Enter your GitHub Personal Access Token" -AsSecureString
$PAT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PAT))

# .env 파일에 PAT 추가/업데이트
$envContent = Get-Content ".env" -Raw
if ($envContent -match "GITHUB_PAT=") {
    # 기존 PAT 업데이트
    $envContent = $envContent -replace "GITHUB_PAT=.*", "GITHUB_PAT=$PAT"
    Set-Content ".env" $envContent
    Write-Host "✅ 기존 PAT가 업데이트되었습니다." -ForegroundColor Green
} else {
    # 새 PAT 추가
    Add-Content ".env" ""
    Add-Content ".env" "# GitHub Personal Access Token"
    Add-Content ".env" "GITHUB_PAT=$PAT"
    Write-Host "✅ PAT가 .env 파일에 저장되었습니다." -ForegroundColor Green
}

# 원격 저장소 URL 업데이트
git remote set-url origin "https://${PAT}@github.com/greensea-lab/green-shipping-ai-server.git"

Write-Host "✅ GitHub PAT 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host "📋 이제 다음 명령어로 Push할 수 있습니다:" -ForegroundColor Yellow
Write-Host "   make push-with-pat-saved" -ForegroundColor White
Write-Host "   또는" -ForegroundColor White
Write-Host "   .\push_with_pat_saved.ps1" -ForegroundColor White 