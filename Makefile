# Green Shipping AI Server - Makefile
# 간단한 명령어로 개발 환경을 관리할 수 있습니다.

.PHONY: help setup local dev prod test clean install-deps migrate migrate-dev migrate-prod migrate-create status

# 기본 타겟
help:
	@echo "🚀 Green Shipping AI Server - 개발 도구"
	@echo ""
	@echo "📋 기본 명령어:"
	@echo "  make setup     - 개발 환경 초기 설정"
	@echo "  make local     - 로컬 개발 서버 실행 (SQLite)"
	@echo "  make dev       - 개발 환경 서버 실행 (원격 MySQL)"
	@echo "  make prod      - 프로덕션 환경 서버 실행 (원격 MySQL)"
	@echo "  make test      - API 테스트 실행"
	@echo "  make status    - 서버 상태 확인"
	@echo "  make clean     - 가상환경 삭제"
	@echo ""
	@echo "🗄️  데이터베이스:"
	@echo "  make migrate                          - 로컬 마이그레이션 적용 (SQLite)"
	@echo "  make migrate-dev                      - 개발 환경 마이그레이션 적용 (MySQL)"
	@echo "  make migrate-prod                     - 프로덕션 마이그레이션 (보안상 제한)"
	@echo "  make migrate-create MESSAGE='설명'    - 새 마이그레이션 생성"
	@echo ""
	@echo "🔐 GitHub Push:"
	@echo "  make push-with-pat                    - PAT를 사용하여 GitHub에 Push"
	@echo "  make push-with-pat-saved              - 저장된 PAT를 사용하여 Push"
	@echo "  make setup-github-pat                 - GitHub PAT 초기 설정"
	@echo "  make check-github-user                - GitHub 사용자 정보 확인"
	@echo "  make check-env                        - 환경별 설정 확인"
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
		if [ -f "env.local" ]; then \
			cp env.local .env; \
			echo "✅ 로컬 환경 설정으로 .env 파일이 생성되었습니다."; \
		elif [ -f "env.example" ]; then \
			cp env.example .env; \
			echo "⚠️  .env 파일이 생성되었습니다. 환경별 설정을 확인해주세요."; \
		fi; \
	fi
	@echo "✅ 개발 환경 설정이 완료되었습니다!"

# 로컬 개발 서버 실행 (SQLite)
local:
	@echo "🚀 로컬 개발 서버를 시작합니다 (SQLite)..."
	@if [ ! -d "venv" ]; then \
		echo "❌ 가상환경이 존재하지 않습니다. 먼저 'make setup'을 실행해주세요."; \
		exit 1; \
	fi
	@if [ -f "env.local" ]; then \
		cp env.local .env; \
		echo "✅ 로컬 환경 설정을 사용합니다."; \
	else \
		echo "⚠️  env.local 파일이 없습니다. 기본 설정을 사용합니다."; \
	fi
	@echo "🔧 서버를 시작합니다..."
	@echo "💡 서버를 중지하려면 Ctrl+C를 누르세요."
	@echo "🌐 서버 주소: http://localhost:8000"
	@echo "📚 API 문서: http://localhost:8000/docs"
	@echo ""
	@venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 개발 환경 서버 실행 (원격 MySQL)
dev:
	@echo "🚀 개발 환경 서버를 시작합니다 (원격 MySQL)..."
	@if [ ! -d "venv" ]; then \
		echo "❌ 가상환경이 존재하지 않습니다. 먼저 'make setup'을 실행해주세요."; \
		exit 1; \
	fi
	@if [ -f "env.dev" ]; then \
		cp env.dev .env; \
		echo "✅ 개발 환경 설정을 사용합니다."; \
	else \
		echo "❌ env.dev 파일이 없습니다. 개발 환경 설정을 확인해주세요."; \
		exit 1; \
	fi
	@echo "🔧 서버를 시작합니다..."
	@echo "💡 서버를 중지하려면 Ctrl+C를 누르세요."
	@echo "🌐 서버 주소: http://localhost:8000"
	@echo "📚 API 문서: http://localhost:8000/docs"
	@echo ""
	@venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 환경 서버 실행 (원격 MySQL)
prod:
	@echo "🚀 프로덕션 환경 서버를 시작합니다 (원격 MySQL)..."
	@echo "⚠️  프로덕션 환경에서 실행 중입니다."
	@if [ ! -d "venv" ]; then \
		echo "❌ 가상환경이 존재하지 않습니다. 먼저 'make setup'을 실행해주세요."; \
		exit 1; \
	fi
	@if [ -f "env.production" ]; then \
		cp env.production .env; \
		echo "✅ 프로덕션 환경 설정을 사용합니다."; \
	else \
		echo "❌ env.production 파일이 없습니다. 프로덕션 환경 설정을 확인해주세요."; \
		exit 1; \
	fi
	@echo "🔧 서버를 시작합니다..."
	@echo "💡 서버를 중지하려면 Ctrl+C를 누르세요."
	@echo "🌐 서버 주소: http://localhost:8000"
	@echo "📚 API 문서: http://localhost:8000/docs"
	@echo ""
	@venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# API 테스트
test:
	@echo "🧪 API 테스트를 실행합니다..."
	@SERVER_STARTED=false; \
	if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ 서버가 실행 중입니다."; \
	else \
		echo "❌ 서버가 실행되지 않았습니다."; \
		echo "🚀 로컬 개발 서버를 자동으로 시작합니다..."; \
		$(MAKE) local & \
		sleep 5; \
		if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
			echo "✅ 서버가 성공적으로 시작되었습니다."; \
			SERVER_STARTED=true; \
		else \
			echo "❌ 서버 시작에 실패했습니다."; \
			echo "💡 수동으로 서버를 시작해주세요: make local"; \
			exit 1; \
		fi; \
	fi; \
	echo "📋 사용 가능한 API 엔드포인트:"; \
	echo "   - 메인 페이지: http://localhost:8000"; \
	echo "   - API 문서: http://localhost:8000/docs"; \
	echo "   - 헬스 체크: http://localhost:8000/health"; \
	echo "   - 사용자 API: http://localhost:8000/api/v1/users/"; \
	echo ""; \
	echo "🧪 API 테스트를 실행합니다..."; \
	curl -s http://localhost:8000/health | python3 -m json.tool; \
	echo ""; \
	echo "✅ API 테스트가 완료되었습니다."; \
	if [ "$$SERVER_STARTED" = "true" ]; then \
		echo "🛑 자동으로 시작된 서버를 종료합니다..."; \
		pkill -f uvicorn; \
		echo "✅ 서버가 종료되었습니다."; \
	fi

# 가상환경 삭제
clean:
	@echo "🧹 가상환경을 삭제합니다..."
	@rm -rf venv
	@echo "✅ 가상환경이 삭제되었습니다."

# 패키지 설치
install-deps:
	@echo "📚 패키지를 설치합니다..."
	@source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ 패키지 설치가 완료되었습니다."

# 데이터베이스 마이그레이션 (로컬 SQLite)
migrate:
	@echo "🗄️  로컬 데이터베이스 마이그레이션을 실행합니다 (SQLite)..."
	@source venv/bin/activate && alembic upgrade head
	@echo "✅ 로컬 마이그레이션이 완료되었습니다."

# 데이터베이스 마이그레이션 (개발 환경 MySQL)
migrate-dev:
	@echo "🗄️  개발 환경 데이터베이스 마이그레이션을 실행합니다 (MySQL)..."
	@if [ -f "env.dev" ]; then \
		echo "📋 개발 환경 설정 파일을 사용합니다."; \
		source venv/bin/activate && DATABASE_URL=$$(grep DATABASE_URL env.dev | cut -d '=' -f2-) alembic upgrade head; \
		echo "✅ 개발 환경 마이그레이션이 완료되었습니다."; \
	else \
		echo "❌ env.dev 파일이 없습니다. 개발 환경 설정을 확인해주세요."; \
	fi

# 프로덕션 마이그레이션 (보안상 제한)
migrate-prod:
	@echo "🚫 프로덕션 마이그레이션은 보안상 로컬에서 실행할 수 없습니다."
	@echo "📋 프로덕션 환경에서 직접 실행하거나 CI/CD 파이프라인을 사용하세요."
	@echo ""
	@echo "💡 대안:"
	@echo "1. 프로덕션 서버에서 직접 실행"
	@echo "2. CI/CD 파이프라인에서 자동 실행"
	@echo "3. 데이터베이스 관리 도구 사용"

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

# 환경별 설정 확인
check-env:
	@echo "🔍 환경별 설정을 확인합니다..."
	@if [ -f "check_env.sh" ]; then \
		chmod +x check_env.sh; \
		./check_env.sh; \
	elif [ -f "check_env.ps1" ]; then \
		echo "Windows PowerShell 스크립트를 사용하세요:"; \
		echo "  .\check_env.ps1"; \
	else \
		echo "❌ check_env.sh 파일이 없습니다."; \
		echo "환경 설정을 수동으로 확인하세요:"; \
		echo "  cat .env"; \
		echo "  ls env.*"; \
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