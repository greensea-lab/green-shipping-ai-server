#!/bin/bash
# Green Shipping AI Server - Unix/Linux Setup Script
# Unix/Linux 환경에서 개발 환경을 설정하는 스크립트

echo "🚀 개발 environment setup..."

# 가상환경 생성
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📚 Installing required packages..."
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# .env 파일 생성
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    if [ -f "env.local" ]; then
        cp env.local .env
        echo "✅ .env file created with local environment settings."
    elif [ -f "env.example" ]; then
        cp env.example .env
        echo "⚠️ .env file created. Please check environment-specific settings."
    fi
fi

echo "✅ Development environment setup completed!" 