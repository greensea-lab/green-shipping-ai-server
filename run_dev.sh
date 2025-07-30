#!/bin/bash
# Green Shipping AI Server - Unix/Linux Development Server Script
# Unix/Linux 환경에서 개발 환경 서버를 실행하는 스크립트

echo "🚀 Starting development server (Remote MySQL)..."

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment does not exist. Please run 'make setup' first."
    exit 1
fi

# 환경 파일 설정
if [ -f "env.dev" ]; then
    cp env.dev .env
    echo "✅ Using development environment settings."
else
    echo "❌ env.dev file not found. Please check development environment settings."
    exit 1
fi

echo "🔧 Starting server..."
echo "💡 Press Ctrl+C to stop the server."
echo "🌐 Server address: http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo ""

# 가상환경 활성화 후 서버 실행
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 