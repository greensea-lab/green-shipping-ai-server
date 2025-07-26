#!/bin/bash

echo "🔐 GitHub PAT Push Script"
echo "=========================="

# PAT 입력 받기
read -s -p "Enter your GitHub Personal Access Token: " PAT
echo

# 원격 저장소 URL 업데이트
git remote set-url origin https://${PAT}@github.com/greensea-lab/green-shipping-ai-server.git

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