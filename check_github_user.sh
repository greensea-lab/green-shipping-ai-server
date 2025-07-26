#!/bin/bash

echo "🔍 GitHub 사용자 정보 확인"
echo "=========================="

echo "📋 현재 Git 설정:"
echo "Name: $(git config --global user.name)"
echo "Email: $(git config --global user.email)"
echo ""

echo "📋 GitHub 프로필 확인 방법:"
echo "1. GitHub.com에 로그인"
echo "2. 우측 상단 프로필 아이콘 클릭"
echo "3. 프로필 페이지에서 'Name' 필드 확인"
echo "4. 또는 Settings → Account → Name 확인"
echo ""

echo "🔧 Git 사용자명 설정:"
echo "git config --global user.name 'Your GitHub Profile Name'"
echo "git config --global user.email 'your.email@example.com'"
echo ""

echo "💡 예시:"
echo "git config --global user.name 'gildong-hong'"
echo "git config --global user.email 'gildong-hong@gmail.com'" 