# Green Shipping AI Server - Makefile
# 간단한 명령어로 개발 환경을 관리할 수 있습니다.

.PHONY: help setup dev test clean install-deps activate

# 기본 타겟
help:
	@echo "🚀 Green Shipping AI Server - 개발 도구"
	@echo ""
	@echo "📋 기본 명령어:"
	@echo "  make setup     - 개발 환경 초기 설정 (가상환경, 패키지 설치, IDE 설정)"
	@echo "  make dev       - 개발 서버 실행 (MySQL)"
	@echo "  make dev-test  - 테스트 서버 실행 (SQLite)"
	@echo "  make test      - API 테스트 실행"
	@echo "  make status    - 서버 상태 확인"
	@echo "  make clean     - 가상환경 삭제"
	@echo "  make activate  - 가상환경 활성화"
	@echo ""
	@echo "📦 의존성 관리:"
	@echo "  make install-deps                     - requirements.txt에서 의존성 설치 (가장 간단)"
	@echo "  make install-package PACKAGE=name     - 새 패키지 설치"
	@echo "  make install-dev-package PACKAGE=name - 개발용 패키지 설치"
	@echo "  make uninstall-package PACKAGE=name   - 패키지 제거"
	@echo "  make update-deps                      - 의존성 업데이트"
	@echo ""
	@echo "🗄️  데이터베이스:"
	@echo "  make migrate                          - 마이그레이션 적용"
	@echo "  make migrate-create MESSAGE='설명'    - 새 마이그레이션 생성"
	@echo ""
	@echo "🎨 코드 품질:"
	@echo "  make format                           - 코드 포맷팅"
	@echo "  make lint                             - 코드 품질 검사"
	@echo "  make test-run                         - 테스트 실행"
	@echo ""
	@echo "🔐 GitHub Push:"
	@echo "  make push-with-pat                    - PAT를 사용하여 GitHub에 Push"
	@echo "  make push-with-pat-saved              - 저장된 PAT를 사용하여 Push"
	@echo "  make setup-github-pat                 - GitHub PAT 초기 설정"
	@echo "  make check-github-user                - GitHub 사용자 정보 확인"
	@echo ""
	@echo "💡 예시:"
	@echo "  make install-package PACKAGE=pandas"
	@echo "  make migrate-create MESSAGE='Add user table'"
	@echo "  make push-with-pat"
	@echo ""

# 개발 환경 초기 설정
setup:
	@echo "🚀 개발 환경을 설정합니다..."
	@if [ ! -d "venv" ]; then \
		echo "📦 Python 가상환경을 생성합니다..."; \
		python3 -m venv venv; \
	fi
	@echo "🔧 가상환경을 활성화합니다..."
	@source venv/bin/activate && pip install --upgrade pip
	@echo "📚 필요한 패키지를 설치합니다..."
	@source venv/bin/activate && pip install -r requirements.txt
	@if [ ! -f ".env" ]; then \
		echo "⚙️  환경 변수 파일을 생성합니다..."; \
		cp env.example .env; \
		echo "⚠️  .env 파일을 확인하고 데이터베이스 설정을 수정해주세요."; \
	fi
	@echo "🎨 IDE 설정 파일을 생성합니다..."
	@mkdir -p .vscode
	@echo '{"python.defaultInterpreterPath": "./venv/bin/python", "python.terminal.activateEnvironment": true}' > .vscode/settings.json
	@echo "✅ 개발 환경 설정이 완료되었습니다!"
	@echo ""
	@echo "📋 다음 단계:"
	@echo "1. MySQL 데이터베이스 설정"
	@echo "2. make dev 로 서버 실행"
	@echo "3. make test 로 API 테스트"

# 개발 서버 실행
dev:
	@echo "🚀 개발 서버를 시작합니다..."
	@echo "📋 가상환경을 활성화하고 서버를 시작합니다..."
	@if [ ! -d "venv" ]; then \
		echo "❌ 가상환경이 존재하지 않습니다. 먼저 'make setup'을 실행해주세요."; \
		exit 1; \
	fi
	@source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 테스트용 서버 실행 (SQLite 사용)
dev-test:
	@echo "🧪 테스트용 서버를 시작합니다 (SQLite)..."
	@echo "📋 가상환경을 활성화하고 테스트 서버를 시작합니다..."
	@if [ ! -d "venv" ]; then \
		echo "❌ 가상환경이 존재하지 않습니다. 먼저 'make setup'을 실행해주세요."; \
		exit 1; \
	fi
	@source venv/bin/activate && DATABASE_URL=sqlite:///./test.db uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API 테스트
test:
	@echo "🧪 API 테스트를 실행합니다..."
	@if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ 서버가 실행 중입니다."; \
		echo "📋 사용 가능한 API 엔드포인트:"; \
		echo "   - 메인 페이지: http://localhost:8000"; \
		echo "   - API 문서: http://localhost:8000/docs"; \
		echo "   - 헬스 체크: http://localhost:8000/health"; \
		echo "   - 사용자 API: http://localhost:8000/api/v1/users/"; \
	else \
		echo "❌ 서버가 실행되지 않았습니다. 먼저 'make dev'로 서버를 시작해주세요."; \
	fi

# 가상환경 삭제
clean:
	@echo "🧹 가상환경을 삭제합니다..."
	@rm -rf venv
	@echo "✅ 가상환경이 삭제되었습니다."

# 패키지만 설치
install-deps:
	@echo "📚 패키지를 설치합니다..."
	@source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ 패키지 설치가 완료되었습니다."

# 가상환경 활성화
activate:
	@echo "🔧 가상환경을 활성화합니다..."
	@echo "source venv/bin/activate"
	@echo "이 명령어를 복사해서 터미널에서 실행하세요."
	@echo ""
	@echo "또는 다음 스크립트를 사용하세요:"
	@echo "  ./activate_venv.sh"

# IDE 터미널용 가상환경 활성화
activate-ide:
	@echo "🔧 IDE 터미널에서 가상환경을 활성화합니다..."
	@if [ -f "activate_venv.sh" ]; then \
		chmod +x activate_venv.sh; \
		./activate_venv.sh; \
	else \
		echo "❌ activate_venv.sh 파일이 없습니다."; \
		echo "make setup을 먼저 실행해주세요."; \
	fi

# 데이터베이스 마이그레이션
migrate:
	@echo "🗄️  데이터베이스 마이그레이션을 실행합니다..."
	@source venv/bin/activate && alembic upgrade head
	@echo "✅ 마이그레이션이 완료되었습니다."

# 새로운 마이그레이션 생성
migrate-create:
	@echo "📝 새로운 마이그레이션을 생성합니다..."
	@echo "사용법: make migrate-create MESSAGE='마이그레이션 설명'"
	@source venv/bin/activate && alembic revision --autogenerate -m "$(MESSAGE)"
	@echo "✅ 마이그레이션이 생성되었습니다."

# 서버 상태 확인
status:
	@echo "📊 서버 상태를 확인합니다..."
	@if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ 서버가 실행 중입니다."; \
		curl -s http://localhost:8000/health | python3 -m json.tool; \
	else \
		echo "❌ 서버가 실행되지 않았습니다."; \
	fi

# 의존성 관리
install-package:
	@echo "📦 새로운 패키지를 설치합니다..."
	@echo "사용법: make install-package PACKAGE=package_name"
	@source venv/bin/activate && pip install $(PACKAGE)
	@source venv/bin/activate && pip freeze > requirements.txt
	@echo "✅ 패키지가 설치되고 requirements.txt가 업데이트되었습니다."

install-dev-package:
	@echo "🔧 개발용 패키지를 설치합니다..."
	@echo "사용법: make install-dev-package PACKAGE=package_name"
	@source venv/bin/activate && pip install $(PACKAGE)
	@source venv/bin/activate && pip freeze > requirements.txt
	@echo "✅ 개발용 패키지가 설치되고 requirements.txt가 업데이트되었습니다."

uninstall-package:
	@echo "🗑️  패키지를 제거합니다..."
	@echo "사용법: make uninstall-package PACKAGE=package_name"
	@source venv/bin/activate && pip uninstall -y $(PACKAGE)
	@source venv/bin/activate && pip freeze > requirements.txt
	@echo "✅ 패키지가 제거되고 requirements.txt가 업데이트되었습니다."

update-deps:
	@echo "📚 모든 의존성을 업데이트합니다..."
	@source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ 의존성이 업데이트되었습니다."

# requirements.txt에서 의존성 설치 (가장 간단한 방법)
install-deps:
	@echo "📦 requirements.txt의 의존성을 설치합니다..."
	@if [ -f "install_deps.sh" ]; then \
		chmod +x install_deps.sh; \
		./install_deps.sh; \
	else \
		echo "❌ install_deps.sh 파일이 없습니다."; \
		echo "make setup을 먼저 실행해주세요."; \
	fi

# 코드 품질 관리
format:
	@echo "🎨 코드를 포맷팅합니다..."
	@source venv/bin/activate && black app/
	@echo "✅ 코드 포맷팅이 완료되었습니다."

lint:
	@echo "🔍 코드 품질을 검사합니다..."
	@source venv/bin/activate && flake8 app/
	@echo "✅ 린팅이 완료되었습니다."

# 테스트
test-run:
	@echo "🧪 테스트를 실행합니다..."
	@source venv/bin/activate && pytest tests/ -v
	@echo "✅ 테스트가 완료되었습니다."

# GitHub 사용자 정보 확인
check-github-user:
	@echo "🔍 GitHub 사용자 정보를 확인합니다..."
	@if [ -f "check_github_user.sh" ]; then \
		chmod +x check_github_user.sh; \
		./check_github_user.sh; \
	elif [ -f "check_github_user.ps1" ]; then \
		echo "Windows PowerShell 스크립트를 사용하세요:"; \
		echo "  .\check_github_user.ps1"; \
	else \
		echo "❌ check_github_user.sh 파일이 없습니다."; \
		echo "Git 사용자 정보를 수동으로 확인하세요:"; \
		echo "  git config --global user.name"; \
		echo "  git config --global user.email"; \
	fi

# GitHub PAT 초기 설정
setup-github-pat:
	@echo "🔐 GitHub PAT를 초기 설정합니다..."
	@if [ -f "setup_github_pat.sh" ]; then \
		chmod +x setup_github_pat.sh; \
		./setup_github_pat.sh; \
	else \
		echo "❌ setup_github_pat.sh 파일이 없습니다."; \
		echo "Windows 사용자는 .\setup_github_pat.ps1을 사용하세요."; \
	fi

# GitHub PAT를 사용한 Push (매번 입력)
push-with-pat:
	@echo "🔐 GitHub PAT를 사용하여 Push합니다..."
	@read -s -p "Enter your GitHub PAT: " pat; \
	git remote set-url origin https://$$pat@github.com/greensea-lab/green-shipping-ai-server.git; \
	git add .; \
	read -p "Enter commit message: " msg; \
	git commit -m "$$msg"; \
	git push origin main; \
	echo "✅ Push completed!"

# 저장된 PAT를 사용한 Push (한 번만 설정)
push-with-pat-saved:
	@echo "🔐 저장된 PAT를 사용하여 Push합니다..."
	@if [ -f "push_with_pat_saved.sh" ]; then \
		chmod +x push_with_pat_saved.sh; \
		./push_with_pat_saved.sh; \
	else \
		echo "❌ push_with_pat_saved.sh 파일이 없습니다."; \
		echo "Windows 사용자는 .\push_with_pat_saved.ps1을 사용하세요."; \
	fi 