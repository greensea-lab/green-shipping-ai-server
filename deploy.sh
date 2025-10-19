#!/bin/bash

# EC2 배포 스크립트
# 로컬에서 실행하여 EC2에 수동 배포할 때 사용

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 환경 변수 확인
if [ -z "$EC2_HOST" ]; then
    echo -e "${RED}❌ EC2_HOST 환경 변수가 설정되지 않았습니다.${NC}"
    echo "사용법: EC2_HOST=your-ec2-ip ./deploy.sh"
    exit 1
fi

EC2_USER=${EC2_USER:-ubuntu}
SSH_KEY=${SSH_KEY:-~/.ssh/id_rsa}
DEPLOY_PATH=${DEPLOY_PATH:-/home/ubuntu/green-shipping-ai-server}

echo -e "${GREEN}🚀 EC2 배포 시작...${NC}"
echo "Host: $EC2_HOST"
echo "User: $EC2_USER"
echo "Path: $DEPLOY_PATH"
echo ""

# SSH 연결 테스트
echo -e "${YELLOW}📡 SSH 연결 테스트...${NC}"
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "${EC2_USER}@${EC2_HOST}" "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${RED}❌ SSH 연결 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ SSH 연결 성공${NC}"
echo ""

# 배포 실행
echo -e "${YELLOW}📦 배포 실행 중...${NC}"
ssh -i "$SSH_KEY" "${EC2_USER}@${EC2_HOST}" << ENDSSH
    set -e
    
    echo "📂 프로젝트 디렉토리로 이동..."
    cd ${DEPLOY_PATH}
    
    echo "📥 최신 코드 가져오기..."
    git fetch origin
    git pull origin \$(git rev-parse --abbrev-ref HEAD)
    
    echo "🛑 기존 컨테이너 중지..."
    docker-compose down
    
    echo "🔨 Docker 이미지 빌드..."
    docker-compose build --no-cache
    
    echo "🚀 컨테이너 시작..."
    docker-compose up -d
    
    echo "⏳ 서비스 준비 대기..."
    sleep 10
    
    echo "📊 서비스 상태 확인..."
    docker-compose ps
    
    echo "🏥 헬스체크..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ 헬스체크 성공!"
            break
        fi
        echo "대기 중... (\$i/30)"
        sleep 2
    done
    
    echo "📋 최근 로그:"
    docker-compose logs --tail=20
ENDSSH

echo ""
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo -e "${GREEN}🌐 서비스 URL: http://${EC2_HOST}:8000${NC}"
echo -e "${GREEN}📚 API 문서: http://${EC2_HOST}:8000/docs${NC}"
