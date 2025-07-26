#!/bin/bash

echo "🔐 GitHub PAT Push (저장된 토큰 사용)"
echo "====================================="

# .env 파일에서 PAT 읽기
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다. 먼저 'make setup'을 실행해주세요."
    exit 1
fi

# PAT 로드
source .env

if [ -z "$GITHUB_PAT" ]; then
    echo "❌ PAT가 설정되지 않았습니다. 먼저 다음 명령어로 설정해주세요:"
    echo "   ./setup_github_pat.sh"
    exit 1
fi

# 원격 저장소 URL 업데이트
git remote set-url origin https://${GITHUB_PAT}@github.com/greensea-lab/green-shipping-ai-server.git

# 변경사항 확인
echo "📋 Current changes:"
git status

# 커밋 메시지 입력
read -p "Enter commit message: " COMMIT_MSG

# 커밋 및 Push
git add .
git commit -m "$COMMIT_MSG"
git push origin main

echo "✅ Push completed successfully!" 