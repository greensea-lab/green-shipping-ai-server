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
	@echo "🚀 개발 environment setup..."
	@if [ ! -d "venv" ]; then \
		echo "📦 Creating Python virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "🔧 Activating virtual environment..."
	@venv/Scripts/pip install --upgrade pip || venv/bin/pip install --upgrade pip
	@echo "📚 Installing required packages..."
	@venv/Scripts/pip install -r requirements.txt || venv/bin/pip install -r requirements.txt
	@if [ ! -f ".env" ]; then \
		echo "⚙️  Creating environment file..."; \
		if [ -f "env.local" ]; then \
			cp env.local .env; \
			echo "✅ .env file created with local environment settings."; \
		elif [ -f "env.example" ]; then \
			cp env.example .env; \
			echo "⚠️  .env file created. Please check environment-specific settings."; \
		fi; \
	fi
	@echo "✅ Development environment setup completed!"

# 로컬 개발 서버 실행 (SQLite)
local:
	@echo "🚀 Starting local development server (SQLite)..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if [ -f "env.local" ]; then \
		cp env.local .env; \
		echo "✅ Using local environment settings."; \
	else \
		echo "⚠️  env.local file not found. Using default settings."; \
	fi
	@echo "🔧 Starting server..."
	@echo "💡 Press Ctrl+C to stop the server."
	@echo "🌐 Server address: http://localhost:8000"
	@echo "📚 API documentation: http://localhost:8000/docs"
	@echo ""
	@venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 || venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 개발 환경 서버 실행 (원격 MySQL)
dev:
	@echo "🚀 Starting development server (Remote MySQL)..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if [ -f "env.dev" ]; then \
		cp env.dev .env; \
		echo "✅ Using development environment settings."; \
	else \
		echo "❌ env.dev file not found. Please check development environment settings."; \
		exit 1; \
	fi
	@echo "🔧 Starting server..."
	@echo "💡 Press Ctrl+C to stop the server."
	@echo "🌐 Server address: http://localhost:8000"
	@echo "📚 API documentation: http://localhost:8000/docs"
	@echo ""
	@venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 || venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 환경 서버 실행 (원격 MySQL)
prod:
	@echo "🚀 Starting production server (Remote MySQL)..."
	@echo "⚠️  Running in production environment."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if [ -f "env.production" ]; then \
		cp env.production .env; \
		echo "✅ Using production environment settings."; \
	else \
		echo "❌ env.production file not found. Please check production environment settings."; \
		exit 1; \
	fi
	@echo "🔧 Starting server..."
	@echo "💡 Press Ctrl+C to stop the server."
	@echo "🌐 Server address: http://localhost:8000"
	@echo "📚 API documentation: http://localhost:8000/docs"
	@echo ""
	@venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 || venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# API 테스트
test:
	@echo "🧪 Running API tests..."
	@SERVER_STARTED=false; \
	if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ Server is running."; \
	else \
		echo "❌ Server is not running."; \
		echo "🚀 Starting local development server automatically..."; \
		$(MAKE) local & \
		sleep 5; \
		if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
			echo "✅ Server started successfully."; \
			SERVER_STARTED=true; \
		else \
			echo "❌ Failed to start server."; \
			echo "💡 Please start server manually: make local"; \
			exit 1; \
		fi; \
	fi; \
	echo "📋 Available API endpoints:"; \
	echo "   - Main page: http://localhost:8000"; \
	echo "   - API docs: http://localhost:8000/docs"; \
	echo "   - Health check: http://localhost:8000/health"; \
	echo "   - Users API: http://localhost:8000/api/v1/users/"; \
	echo ""; \
	echo "🧪 Running API tests..."; \
	curl -s http://localhost:8000/health | python3 -m json.tool; \
	echo ""; \
	echo "✅ API tests completed."; \
	if [ "$$SERVER_STARTED" = "true" ]; then \
		echo "🛑 Stopping automatically started server..."; \
		pkill -f uvicorn; \
		echo "✅ Server stopped."; \
	fi

# 가상환경 삭제
clean:
	@echo "🧹 Removing virtual environment..."
	@rm -rf venv
	@echo "✅ Virtual environment removed."

# 패키지 설치
install-deps:
	@echo "📚 Installing packages..."
	@venv/Scripts/pip install -r requirements.txt || venv/bin/pip install -r requirements.txt
	@echo "✅ Package installation completed."

# 데이터베이스 마이그레이션 (로컬 SQLite)
migrate:
	@echo "🗄️  Running local database migration (SQLite)..."
	@venv/Scripts/alembic upgrade head || venv/bin/alembic upgrade head
	@echo "✅ Local migration completed."

# 데이터베이스 마이그레이션 (개발 환경 MySQL)
migrate-dev:
	@echo "🗄️  Running development database migration (MySQL)..."
	@if [ -f "env.dev" ]; then \
		echo "📋 Using development environment settings."; \
		venv/Scripts/alembic upgrade head || venv/bin/alembic upgrade head; \
		echo "✅ Development migration completed."; \
	else \
		echo "❌ env.dev file not found. Please check development environment settings."; \
	fi

# 프로덕션 마이그레이션 (보안상 제한)
migrate-prod:
	@echo "🚫 Production migration cannot be run locally for security reasons."
	@echo "📋 Run directly in production environment or use CI/CD pipeline."
	@echo ""
	@echo "💡 Alternatives:"
	@echo "1. Run directly on production server"
	@echo "2. Automatic execution in CI/CD pipeline"
	@echo "3. Use database management tools"

# 새로운 마이그레이션 생성
migrate-create:
	@echo "📝 Creating new migration..."
	@echo "Usage: make migrate-create MESSAGE='migration description'"
	@venv/Scripts/alembic revision --autogenerate -m "$(MESSAGE)" || venv/bin/alembic revision --autogenerate -m "$(MESSAGE)"
	@echo "✅ Migration created."

# 서버 상태 확인
status:
	@echo "📊 Checking server status..."
	@if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ Server is running."; \
		curl -s http://localhost:8000/health | python3 -m json.tool; \
	else \
		echo "❌ Server is not running."; \
	fi

# GitHub 사용자 정보 확인
check-github-user:
	@echo "🔍 Checking GitHub user information..."
	@if [ -f "check_github_user.sh" ]; then \
		chmod +x check_github_user.sh; \
		./check_github_user.sh; \
	elif [ -f "check_github_user.ps1" ]; then \
		echo "Use Windows PowerShell script:"; \
		echo "  .\check_github_user.ps1"; \
	else \
		echo "❌ check_github_user.sh file not found."; \
		echo "Check Git user information manually:"; \
		echo "  git config --global user.name"; \
		echo "  git config --global user.email"; \
	fi

# 환경별 설정 확인
check-env:
	@echo "🔍 Checking environment settings..."
	@if [ -f "check_env.sh" ]; then \
		chmod +x check_env.sh; \
		./check_env.sh; \
	elif [ -f "check_env.ps1" ]; then \
		echo "Use Windows PowerShell script:"; \
		echo "  .\check_env.ps1"; \
	else \
		echo "❌ check_env.sh file not found."; \
		echo "Check environment settings manually:"; \
		echo "  cat .env"; \
		echo "  ls env.*"; \
	fi

# GitHub PAT 초기 설정
setup-github-pat:
	@echo "🔐 Setting up GitHub PAT..."
	@if [ -f "setup_github_pat.sh" ]; then \
		chmod +x setup_github_pat.sh; \
		./setup_github_pat.sh; \
	else \
		echo "❌ setup_github_pat.sh file not found."; \
		echo "Windows users should use .\setup_github_pat.ps1"; \
	fi

# GitHub PAT를 사용한 Push (매번 입력)
push-with-pat:
	@echo "🔐 Pushing with GitHub PAT..."
	@read -s -p "Enter your GitHub PAT: " pat; \
	git remote set-url origin https://$$pat@github.com/greensea-lab/green-shipping-ai-server.git; \
	git add .; \
	read -p "Enter commit message: " msg; \
	git commit -m "$$msg"; \
	git push origin main; \
	echo "✅ Push completed!"

# 저장된 PAT를 사용한 Push (한 번만 설정)
push-with-pat-saved:
	@echo "🔐 Pushing with saved PAT..."
	@if [ -f "push_with_pat_saved.sh" ]; then \
		chmod +x push_with_pat_saved.sh; \
		./push_with_pat_saved.sh; \
	else \
		echo "❌ push_with_pat_saved.sh file not found."; \
		echo "Windows users should use .\push_with_pat_saved.ps1"; \
	fi 