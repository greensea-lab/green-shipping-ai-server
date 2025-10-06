#!/bin/bash

# EC2 초기 설정 스크립트
# EC2 인스턴스에서 최초 1회 실행

set -e

echo "🚀 EC2 초기 설정 시작..."

# 시스템 업데이트
echo "📦 시스템 업데이트..."
sudo apt update
sudo apt upgrade -y

# Docker 설치
echo "🐳 Docker 설치..."
if ! command -v docker &> /dev/null; then
    sudo apt install -y docker.io docker-compose git curl
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "✅ Docker 설치 완료"
else
    echo "✅ Docker가 이미 설치되어 있습니다"
fi

# Docker Compose 버전 확인
echo "📋 Docker Compose 버전 확인..."
docker-compose --version

# 프로젝트 클론
REPO_URL="https://github.com/greensea-lab/green-shipping-ai-server.git"
PROJECT_DIR="$HOME/green-shipping-ai-server"

if [ -d "$PROJECT_DIR" ]; then
    echo "📂 프로젝트가 이미 존재합니다: $PROJECT_DIR"
    cd "$PROJECT_DIR"
    git pull origin develop
else
    echo "📥 프로젝트 클론..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# .env 파일 생성
if [ ! -f ".env" ]; then
    echo "📝 .env 파일 생성..."
    
    # 보안 키 생성
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    INTERNAL_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    MYSQL_ROOT_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
    MYSQL_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
    
    cat > .env << EOF
# ===== Database (Docker Compose) =====
DATABASE_URL=mysql+pymysql://green_user:${MYSQL_PASSWORD}@db:3306/green_shipping_db

# ===== Security =====
SECRET_KEY=${SECRET_KEY}
INTERNAL_API_TOKEN=${INTERNAL_TOKEN}

# ===== Server =====
HOST=0.0.0.0
PORT=8000
DEBUG=False
ENVIRONMENT=production

# ===== AI / LLM (선택) =====
OPENAI_API_KEY=
AI_MODEL=gpt-5
AI_TEMPERATURE=1.0
AI_MAX_TOKENS=1000
EMBEDDING_MODEL=text-embedding-3-small

# ===== RAG =====
RAG_PERSIST_DIR=/app/data/chroma

# ===== MySQL Container =====
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_DATABASE=green_shipping_db
MYSQL_USER=green_user
MYSQL_PASSWORD=${MYSQL_PASSWORD}
EOF
    
    echo "✅ .env 파일이 생성되었습니다"
    echo ""
    echo "⚠️  OpenAI API 키를 추가하려면:"
    echo "   nano .env"
    echo "   OPENAI_API_KEY=sk-proj-your-key 수정"
else
    echo "✅ .env 파일이 이미 존재합니다"
fi

# 디렉토리 생성
echo "📁 필요한 디렉토리 생성..."
mkdir -p data reports kb

# Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드..."
docker-compose build

# 컨테이너 시작
echo "🚀 컨테이너 시작..."
docker-compose up -d

# 서비스 준비 대기
echo "⏳ 서비스 준비 대기..."
sleep 15

# 헬스체크
echo "🏥 헬스체크..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 헬스체크 성공!"
        break
    fi
    echo "대기 중... ($i/30)"
    sleep 2
done

# 상태 확인
echo ""
echo "📊 서비스 상태:"
docker-compose ps

echo ""
echo "✅ EC2 초기 설정 완료!"
echo ""