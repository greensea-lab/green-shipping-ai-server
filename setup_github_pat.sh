#!/bin/bash

echo "🔐 GitHub PAT 초기 설정"
echo "========================"

# .env 파일에 PAT 저장 (gitignore에 포함됨)
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다. 먼저 'make setup'을 실행해주세요."
    exit 1
fi

# PAT 입력 받기
read -s -p "Enter your GitHub Personal Access Token: " PAT
echo

# .env 파일에 PAT 추가
if grep -q "GITHUB_PAT" .env; then
    # 기존 PAT 업데이트
    sed -i.bak "s/GITHUB_PAT=.*/GITHUB_PAT=$PAT/" .env
    echo "✅ 기존 PAT가 업데이트되었습니다."
else
    # 새 PAT 추가
    echo "" >> .env
    echo "# GitHub Personal Access Token" >> .env
    echo "GITHUB_PAT=$PAT" >> .env
    echo "✅ PAT가 .env 파일에 저장되었습니다."
fi

# 원격 저장소 URL 업데이트
git remote set-url origin https://${PAT}@github.com/greensea-lab/green-shipping-ai-server.git

echo "✅ GitHub PAT 설정이 완료되었습니다!"
echo "📋 이제 다음 명령어로 Push할 수 있습니다:"
echo "   make push-with-pat-saved"
echo "   또는"
echo "   ./push_with_pat_saved.sh" 