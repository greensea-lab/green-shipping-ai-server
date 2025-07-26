#!/bin/bash

# Green Shipping AI Server - Development Environment Setup
# 이 스크립트는 개발 환경을 자동으로 설정합니다.

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 Green Shipping AI Server 개발 환경 설정을 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 1. Python 가상환경 확인 및 생성
print_step "Python 가상환경 설정 중..."

if [ ! -d "venv" ]; then
    echo "가상환경을 생성합니다..."
    python3 -m venv venv
    print_success "가상환경이 생성되었습니다."
else
    print_success "가상환경이 이미 존재합니다."
fi

# 2. 가상환경 활성화
print_step "가상환경을 활성화합니다..."
source venv/bin/activate
print_success "가상환경이 활성화되었습니다."

# 3. pip 업그레이드
print_step "pip를 최신 버전으로 업그레이드합니다..."
pip install --upgrade pip

# 4. 의존성 설치
print_step "필요한 패키지들을 설치합니다..."
pip install -r requirements.txt
print_success "모든 패키지가 설치되었습니다."

# 5. 환경별 설정 파일 확인
print_step "환경별 설정 파일을 확인합니다..."

# 환경별 설정 파일 존재 여부 확인
if [ -f "env.local" ]; then
    print_success "로컬 환경 설정 파일 (env.local)이 존재합니다."
fi

if [ -f "env.dev" ]; then
    print_success "개발 환경 설정 파일 (env.dev)이 존재합니다."
fi

if [ -f "env.production" ]; then
    print_success "프로덕션 환경 설정 파일 (env.production)이 존재합니다."
fi

# 기본 .env 파일 설정 (로컬 환경으로 초기화)
if [ ! -f ".env" ]; then
    if [ -f "env.local" ]; then
        cp env.local .env
        print_success "로컬 환경 설정으로 .env 파일이 생성되었습니다."
    elif [ -f "env.example" ]; then
        cp env.example .env
        print_warning ".env 파일이 생성되었습니다. 환경별 설정을 확인해주세요."
    else
        print_error "환경 설정 파일을 찾을 수 없습니다."
        exit 1
    fi
else
    print_success ".env 파일이 이미 존재합니다."
fi

print_step "환경별 서버 실행 방법:"
echo "  - 로컬 환경: make local (SQLite 사용)"
echo "  - 개발 환경: make dev (원격 MySQL 사용)"
echo "  - 프로덕션 환경: make prod (원격 MySQL 사용)"

# 6. IDE 설정 파일 생성
print_step "IDE 설정 파일을 생성합니다..."

# VS Code 설정
if [ ! -d ".vscode" ]; then
    mkdir .vscode
fi

cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.analysis.autoImportCompletions": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "venv": false
    }
}
EOF

# VS Code launch.json (디버깅 설정)
cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "console": "integratedTerminal",
            "python": "./venv/bin/python",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}"
            }
        }
    ]
}
EOF

print_success "VS Code 설정이 완료되었습니다."

# 7. PyCharm 설정 파일 생성
if [ ! -d ".idea/runConfigurations" ]; then
    mkdir -p .idea/runConfigurations
fi

cat > .idea/runConfigurations/FastAPI.xml << EOF
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="FastAPI" type="PythonConfigurationType" factoryName="Python">
    <module name="green-shipping-ai-server" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <envs>
      <env name="PYTHONPATH" value="\$PROJECT_DIR\$" />
    </envs>
    <option name="SDK_HOME" value="\$PROJECT_DIR\$/venv/bin/python" />
    <option name="WORKING_DIRECTORY" value="\$PROJECT_DIR\$" />
    <option name="IS_MODULE_SDK" value="true" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <option name="SCRIPT_NAME" value="\$PROJECT_DIR\$/venv/bin/uvicorn" />
    <option name="PARAMETERS" value="app.main:app --reload --host 0.0.0.0 --port 8000" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="false" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>
EOF

print_success "PyCharm 설정이 완료되었습니다."

# 8. 개발용 스크립트 생성
print_step "개발용 스크립트를 생성합니다..."

cat > dev.sh << 'EOF'
#!/bin/bash
# 개발 서버 실행 스크립트

echo "🚀 Green Shipping AI Server 개발 서버를 시작합니다..."

# 가상환경 활성화
source venv/bin/activate

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

chmod +x dev.sh

cat > test_api.sh << 'EOF'
#!/bin/bash
# API 테스트 스크립트

echo "🧪 API 테스트를 실행합니다..."

# 서버가 실행 중인지 확인
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ 서버가 실행되지 않았습니다. 먼저 ./dev.sh로 서버를 시작해주세요."
    exit 1
fi

echo "✅ 서버가 실행 중입니다."
echo "📋 사용 가능한 API 엔드포인트:"
echo "   - 메인 페이지: http://localhost:8000"
echo "   - API 문서: http://localhost:8000/docs"
echo "   - 헬스 체크: http://localhost:8000/health"
echo "   - 사용자 API: http://localhost:8000/api/v1/users/"
EOF

chmod +x test_api.sh

# 가상환경 활성화 스크립트 생성
cat > activate_venv.sh << 'EOF'
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
EOF

chmod +x activate_venv.sh

# 의존성 설치 스크립트 생성
cat > install_deps.sh << 'EOF'
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
EOF

chmod +x install_deps.sh

print_success "개발용 스크립트가 생성되었습니다."

# 9. 완료 메시지
echo ""
echo -e "${GREEN}🎉 개발 환경 설정이 완료되었습니다!${NC}"
echo ""
echo "📋 다음 단계:"
echo "1. 데이터베이스 설정:"
echo "   - MySQL 서버 시작"
echo "   - 데이터베이스 생성: CREATE DATABASE green_shipping_db;"
echo ""
echo "2. 서버 실행:"
echo "   ./dev.sh"
echo ""
echo "3. API 테스트:"
echo "   ./test_api.sh"
echo ""
echo "4. IDE에서 프로젝트 열기:"
echo "   - VS Code: code ."
echo "   - PyCharm: 프로젝트 폴더 열기"
echo ""
echo "📚 자세한 내용은 README.md를 참고하세요."
echo "" 