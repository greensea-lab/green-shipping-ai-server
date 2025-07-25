#!/bin/bash

# Green Shipping AI Server - 의존성 설치 스크립트
# requirements.txt에 추가된 패키지들을 자동으로 설치합니다.

set -e

echo "📦 Green Shipping AI Server 의존성 설치를 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 함수 정의
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. 가상환경 확인
print_step "가상환경을 확인합니다..."

if [ ! -d "venv" ]; then
    print_error "가상환경이 존재하지 않습니다."
    echo "다음 명령어로 가상환경을 생성해주세요:"
    echo "  make setup"
    echo "  또는"
    echo "  ./setup_dev.sh"
    exit 1
fi

# 2. 가상환경 활성화
print_step "가상환경을 활성화합니다..."
source venv/bin/activate
print_success "가상환경이 활성화되었습니다."

# 3. requirements.txt 확인
print_step "requirements.txt 파일을 확인합니다..."

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt 파일이 존재하지 않습니다."
    exit 1
fi

# 4. 현재 설치된 패키지 백업
print_step "현재 설치된 패키지를 백업합니다..."
pip freeze > requirements_backup.txt
print_success "백업이 완료되었습니다: requirements_backup.txt"

# 5. 새로운 패키지 설치
print_step "requirements.txt의 패키지들을 설치합니다..."
pip install -r requirements.txt

# 6. 설치 결과 확인
print_step "설치 결과를 확인합니다..."
echo ""
echo "📊 설치된 패키지 목록:"
pip list

echo ""
print_success "의존성 설치가 완료되었습니다!"
echo ""
echo "📋 다음 단계:"
echo "1. 서버 실행: make dev"
echo "2. API 테스트: make test"
echo "3. 서버 상태 확인: make status"
echo ""
echo "💡 문제가 발생하면 다음 명령어로 백업에서 복원할 수 있습니다:"
echo "  pip install -r requirements_backup.txt" 