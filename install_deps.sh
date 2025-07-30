#!/bin/bash
# Green Shipping AI Server - Unix/Linux Package Installation Script
# Unix/Linux 환경에서 패키지를 설치하는 스크립트

echo "📚 Installing packages..."

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment does not exist. Please run 'make setup' first."
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
venv/bin/pip install --upgrade pip

# 패키지 설치
venv/bin/pip install -r requirements.txt

echo "✅ Package installation completed!" 