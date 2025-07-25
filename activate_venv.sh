#!/bin/bash

# Green Shipping AI Server - 가상환경 활성화 스크립트
# IDE 터미널에서 이 스크립트를 실행하면 가상환경이 활성화됩니다.

echo "🔧 Green Shipping AI Server 가상환경을 활성화합니다..."

# 현재 디렉토리가 프로젝트 루트인지 확인
if [ ! -f "requirements.txt" ] || [ ! -d "app" ]; then
    echo "❌ 현재 디렉토리가 Green Shipping AI Server 프로젝트가 아닙니다."
    echo "프로젝트 루트 디렉토리로 이동해주세요."
    exit 1
fi

# 가상환경이 존재하는지 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 존재하지 않습니다."
    echo "다음 명령어로 가상환경을 생성해주세요:"
    echo "  make setup"
    echo "  또는"
    echo "  ./setup_dev.sh"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# 활성화 확인
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ 가상환경이 활성화되었습니다: $VIRTUAL_ENV"
    echo "🐍 Python 경로: $(which python)"
    echo "📦 pip 경로: $(which pip)"
    echo ""
    echo "📋 사용 가능한 명령어:"
    echo "  make dev      # 개발 서버 실행"
    echo "  make test     # API 테스트"
    echo "  make status   # 서버 상태 확인"
    echo ""
    echo "💡 이 터미널을 닫으면 가상환경이 비활성화됩니다."
else
    echo "❌ 가상환경 활성화에 실패했습니다."
    exit 1
fi 