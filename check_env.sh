#!/bin/bash

# Green Shipping AI Server - 환경별 설정 확인 스크립트
# 현재 환경 설정과 사용 가능한 환경들을 확인합니다.

echo "🔍 Green Shipping AI Server 환경별 설정 확인"
echo "=========================================="

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

# 1. 현재 환경 확인
print_step "현재 환경 설정 확인"

if [ -f ".env" ]; then
    print_success ".env 파일이 존재합니다."
    
    # DATABASE_URL 확인
    if grep -q "DATABASE_URL" .env; then
        DB_URL=$(grep "DATABASE_URL" .env | cut -d '=' -f2-)
        if [[ $DB_URL == *"sqlite"* ]]; then
            print_success "현재 설정: SQLite (로컬 환경)"
        elif [[ $DB_URL == *"mysql"* ]]; then
            if grep -q "DEBUG=True" .env; then
                print_success "현재 설정: MySQL (개발 환경)"
            else
                print_warning "현재 설정: MySQL (프로덕션 환경)"
            fi
        else
            print_warning "현재 설정: 알 수 없는 데이터베이스"
        fi
    else
        print_error "DATABASE_URL이 설정되지 않았습니다."
    fi
else
    print_error ".env 파일이 없습니다."
fi

echo ""

# 2. 환경별 설정 파일 확인
print_step "환경별 설정 파일 확인"

# 로컬 환경
if [ -f "env.local" ]; then
    print_success "env.local (로컬 환경) - 존재"
    if grep -q "sqlite" env.local; then
        print_success "  → SQLite 데이터베이스 사용"
    fi
else
    print_error "env.local (로컬 환경) - 없음"
fi

# 개발 환경
if [ -f "env.dev" ]; then
    print_success "env.dev (개발 환경) - 존재"
    if grep -q "mysql" env.dev; then
        print_success "  → MySQL 데이터베이스 사용"
    fi
else
    print_error "env.dev (개발 환경) - 없음"
fi

# 프로덕션 환경
if [ -f "env.production" ]; then
    print_success "env.production (프로덕션 환경) - 존재"
    if grep -q "mysql" env.production; then
        print_success "  → MySQL 데이터베이스 사용"
    fi
else
    print_error "env.production (프로덕션 환경) - 없음"
fi

echo ""

# 3. 사용 가능한 명령어
print_step "사용 가능한 환경별 명령어"

echo "📋 서버 실행:"
echo "  make local  # 로컬 환경 (SQLite)"
echo "  make dev        # 개발 환경 (원격 MySQL)"
echo "  make prod       # 프로덕션 환경 (원격 MySQL)"
echo ""

echo "📋 마이그레이션:"
echo "  make migrate    # 로컬 마이그레이션 (SQLite)"
echo "  make migrate-dev # 개발 환경 마이그레이션 (MySQL)"
echo "  make migrate-prod # 프로덕션 마이그레이션 (보안상 제한)"
echo ""

# 4. 환경 전환 방법
print_step "환경 전환 방법"

echo "💡 환경을 변경하려면:"
echo "  1. 원하는 환경 설정 파일을 .env로 복사"
echo "  2. 해당 환경의 서버 실행 명령어 사용"
echo ""
echo "예시:"
echo "  cp env.dev .env && make dev"
echo "  cp env.local .env && make local"
echo ""

# 5. 현재 상태 요약
print_step "현재 상태 요약"

if [ -f ".env" ]; then
    if grep -q "sqlite" .env; then
        echo "🎯 현재 환경: 로컬 (SQLite)"
        echo "💡 권장 명령어: make local"
    elif grep -q "mysql" .env; then
        if grep -q "DEBUG=True" .env; then
            echo "🎯 현재 환경: 개발 (MySQL)"
            echo "💡 권장 명령어: make dev"
        else
            echo "🎯 현재 환경: 프로덕션 (MySQL)"
            echo "💡 권장 명령어: make prod"
        fi
    fi
else
    echo "🎯 현재 환경: 설정되지 않음"
    echo "💡 권장 명령어: make setup"
fi

echo ""
print_success "환경 확인이 완료되었습니다!" 