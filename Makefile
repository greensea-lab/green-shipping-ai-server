# Green Shipping AI Server - Makefile
# 간단한 명령어로 개발 환경을 관리할 수 있습니다.

# 환경 감지 및 설정
# Git Bash, Windows CMD/PowerShell, Unix/Linux 모든 환경 지원
SHELL := /bin/bash
UNAME_O := $(shell uname -o 2>/dev/null)
UNAME_S := $(shell uname -s 2>/dev/null)

# 환경별 설정
ifeq ($(UNAME_O),Msys)
    # Git Bash 환경
    DETECTED_OS := GitBash
    PYTHON := python
    VENV_BIN := venv/Scripts
    VENV_PYTHON := $(VENV_BIN)/python
    VENV_PIP := $(VENV_BIN)/pip
    VENV_ALEMBIC := $(VENV_BIN)/alembic
    RM := rm -rf
    MKDIR := mkdir -p
    COPY := cp
    EXISTS_FILE = [ -f "$(1)" ]
    EXISTS_DIR = [ -d "$(1)" ]
    HTTP_TEST := curl -s
    JSON_PRETTY := python -m json.tool
else ifeq ($(OS),Windows_NT)
    # Windows CMD/PowerShell
    DETECTED_OS := Windows
    PYTHON := python
    VENV_BIN := venv\\Scripts
    VENV_PYTHON := $(VENV_BIN)\\python
    VENV_PIP := $(VENV_BIN)\\pip
    VENV_ALEMBIC := $(VENV_BIN)\\alembic
    RM := rmdir /s /q
    MKDIR := mkdir
    COPY := copy
    EXISTS_FILE = exist "$(1)"
    EXISTS_DIR = exist "$(1)"
    HTTP_TEST := powershell -Command "try { Invoke-RestMethod -Uri"
    JSON_PRETTY := python -m json.tool
else
    # Unix/Linux/macOS
    DETECTED_OS := Unix
    PYTHON := python3
    VENV_BIN := venv/bin
    VENV_PYTHON := $(VENV_BIN)/python
    VENV_PIP := $(VENV_BIN)/pip
    VENV_ALEMBIC := $(VENV_BIN)/alembic
    RM := rm -rf
    MKDIR := mkdir -p
    COPY := cp
    EXISTS_FILE = [ -f "$(1)" ]
    EXISTS_DIR = [ -d "$(1)" ]
    HTTP_TEST := curl -s
    JSON_PRETTY := python3 -m json.tool
endif

.PHONY: help setup local dev prod test clean install-deps migrate migrate-dev migrate-prod migrate-create status

# 기본 타겟
help:
	@echo "🚀 Green Shipping AI Server - 개발 도구"
	@echo ""
	@echo "🖥️  감지된 환경: $(DETECTED_OS)"
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
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if $(call EXISTS_DIR,venv); then \
		echo "⚠️  Virtual environment already exists."; \
	else \
		echo "📦 Creating virtual environment..."; \
		$(PYTHON) -m venv venv || (echo "❌ Failed to create venv. Install python venv: pip install virtualenv" && exit 1); \
	fi
	@echo "📚 Upgrading pip..."
	@$(VENV_PIP) install --upgrade pip
	@if $(call EXISTS_FILE,requirements.txt); then \
		echo "📦 Installing dependencies..."; \
		$(VENV_PIP) install -r requirements.txt; \
		echo "✅ Dependencies installed."; \
	else \
		echo "⚠️  requirements.txt not found. Skipping dependency installation."; \
	fi
	@echo "✅ Setup completed."

# 로컬 개발 서버 실행 (SQLite)
local:
	@echo "🚀 Starting local development server (SQLite)..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if ! $(call EXISTS_DIR,venv); then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if $(call EXISTS_FILE,env.local); then \
		$(COPY) env.local .env; \
		echo "✅ Using local environment settings."; \
	else \
		echo "⚠️  env.local file not found. Using default settings."; \
	fi
	@echo "🔧 Starting server..."
	@echo "💡 Press Ctrl+C to stop the server."
	@echo "🌐 Server address: http://localhost:8000"
	@echo "📚 API documentation: http://localhost:8000/docs"
	@echo ""
	@$(VENV_PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 개발 환경 서버 실행 (원격 MySQL)
dev:
	@echo "🚀 Starting development server (Remote MySQL)..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if ! $(call EXISTS_DIR,venv); then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if $(call EXISTS_FILE,env.dev); then \
		$(COPY) env.dev .env; \
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
	@$(VENV_PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 프로덕션 환경 서버 실행 (원격 MySQL)
prod:
	@echo "🚀 Starting production server (Remote MySQL)..."
	@echo "⚠️  Running in production environment."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if ! $(call EXISTS_DIR,venv); then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if $(call EXISTS_FILE,env.production); then \
		$(COPY) env.production .env; \
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
	@$(VENV_PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# API 테스트
test:
	@echo "🧪 Running API tests..."
	@echo "🖥️  환경: $(DETECTED_OS)"
ifeq ($(DETECTED_OS),Windows)
	@powershell -Command "try { Invoke-RestMethod -Uri http://localhost:8000/health -Method Get | Out-Null; Write-Host '✅ Server is running.' } catch { Write-Host '❌ Server is not running. Please start server: make local'; exit 1 }"
	@echo "📋 Available API endpoints:"
	@echo "   - Main page: http://localhost:8000"
	@echo "   - API docs: http://localhost:8000/docs"
	@echo "   - Health check: http://localhost:8000/health"
	@echo "   - Users API: http://localhost:8000/api/v1/users/"
	@echo ""
	@echo "🧪 Running API tests..."
	@powershell -Command "Invoke-RestMethod -Uri http://localhost:8000/health -Method Get | ConvertTo-Json"
	@echo ""
	@echo "✅ API tests completed."
else
	@if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ Server is running."; \
	else \
		echo "❌ Server is not running. Please start server: make local"; \
		exit 1; \
	fi
	@echo "📋 Available API endpoints:"
	@echo "   - Main page: http://localhost:8000"
	@echo "   - API docs: http://localhost:8000/docs"
	@echo "   - Health check: http://localhost:8000/health"
	@echo "   - Users API: http://localhost:8000/api/v1/users/"
	@echo ""
	@echo "🧪 Running API tests..."
	@curl -s http://localhost:8000/health | $(JSON_PRETTY)
	@echo ""
	@echo "✅ API tests completed."
endif

# 가상환경 삭제
clean:
	@echo "🧹 Removing virtual environment..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if $(call EXISTS_DIR,venv); then \
		$(RM) venv; \
		echo "✅ Virtual environment removed."; \
	else \
		echo "⚠️  Virtual environment does not exist."; \
	fi
	@if $(call EXISTS_FILE,.env); then \
		rm -f .env; \
		echo "✅ .env file removed."; \
	fi
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed."

# 패키지 설치
install-deps:
	@echo "📚 Installing packages..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if ! $(call EXISTS_DIR,venv); then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if $(call EXISTS_FILE,requirements.txt); then \
		$(VENV_PIP) install -r requirements.txt; \
		echo "✅ Packages installed."; \
	else \
		echo "❌ requirements.txt file not found."; \
		exit 1; \
	fi

# 데이터베이스 마이그레이션 (로컬 SQLite)
migrate:
	@echo "🗄️  Running local database migration (SQLite)..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if ! $(call EXISTS_DIR,venv); then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@$(VENV_ALEMBIC) upgrade head
	@echo "✅ Local migration completed."

# 데이터베이스 마이그레이션 (개발 환경 MySQL)
migrate-dev:
	@echo "🗄️  Running development database migration (MySQL)..."ls -l
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if ! $(call EXISTS_DIR,venv); then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@if $(call EXISTS_FILE,env.dev); then \
		echo "📋 Using development environment settings."; \
		$(COPY) env.dev .env;
		$(VENV_ALEMBIC) upgrade head; \
		echo "✅ Development migration completed."; \
	else \
		echo "❌ env.dev file not found. Please check development environment settings."; \
		exit 1; \
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
ifndef MESSAGE
	@echo "❌ Usage: make migrate-create MESSAGE='migration description'"
	@exit 1
endif
	@echo "🖥️  환경: $(DETECTED_OS)"
	@if ! $(call EXISTS_DIR,venv); then \
		echo "❌ Virtual environment does not exist. Please run 'make setup' first."; \
		exit 1; \
	fi
	@$(VENV_ALEMBIC) revision --autogenerate -m "$(MESSAGE)"
	@echo "✅ Migration created: $(MESSAGE)"

# 서버 상태 확인
status:
	@echo "📊 Checking server status..."
	@echo "🖥️  환경: $(DETECTED_OS)"
ifeq ($(DETECTED_OS),Windows)
	@powershell -Command "try { $$response = Invoke-RestMethod -Uri http://localhost:8000/health -Method Get; Write-Host '✅ Server is running.'; $$response | ConvertTo-Json } catch { Write-Host '❌ Server is not running.' }"
else
	@if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ Server is running."; \
		curl -s http://localhost:8000/health | $(JSON_PRETTY); \
	else \
		echo "❌ Server is not running."; \
	fi
endif

# GitHub 사용자 정보 확인
check-github-user:
	@echo "🔍 Checking GitHub user information..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@echo "📋 Git user configuration:"
	@git config --global user.name || echo "❌ Git user.name not set"
	@git config --global user.email || echo "❌ Git user.email not set"
	@echo ""
	@echo "💡 To set Git user info:"
	@echo "  git config --global user.name 'Your Name'"
	@echo "  git config --global user.email 'your.email@example.com'"

# 환경별 설정 확인
check-env:
	@echo "🔍 Checking environment settings..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@echo "📋 Available environment files:"
	@ls -la env.* 2>/dev/null || echo "❌ No env.* files found"
	@echo ""
	@echo "📋 Current .env file:"
	@if $(call EXISTS_FILE,.env); then \
		echo "✅ .env file exists"; \
		head -5 .env 2>/dev/null || echo "❌ Cannot read .env file"; \
	else \
		echo "❌ .env file not found"; \
	fi

# GitHub PAT 초기 설정
setup-github-pat:
	@echo "🔐 Setting up GitHub PAT..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@echo "💡 Please create a GitHub Personal Access Token:"
	@echo "1. Go to https://github.com/settings/tokens"
	@echo "2. Click 'Generate new token (classic)'"
	@echo "3. Select scopes: repo, workflow"
	@echo "4. Copy the token and use it with 'make push-with-pat'"

# GitHub PAT를 사용한 Push (매번 입력)
push-with-pat:
	@echo "🔐 Pushing with GitHub PAT..."
	@echo "🖥️  환경: $(DETECTED_OS)"
ifeq ($(DETECTED_OS),Windows)
	@powershell -Command "$$pat = Read-Host 'Enter your GitHub PAT' -AsSecureString; $$pat_plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($$pat)); git remote set-url origin https://$$pat_plain@github.com/greensea-lab/green-shipping-ai-server.git; git add .; $$msg = Read-Host 'Enter commit message'; git commit -m \"$$msg\"; git push origin main; Write-Host '✅ Push completed!'"
else
	@read -s -p "Enter your GitHub PAT: " pat; echo ""; \
	git remote set-url origin https://$$pat@github.com/greensea-lab/green-shipping-ai-server.git; \
	git add .; \
	read -p "Enter commit message: " msg; \
	git commit -m "$$msg"; \
	git push origin main; \
	echo "✅ Push completed!"
endif

# 저장된 PAT를 사용한 Push (한 번만 설정)
push-with-pat-saved:
	@echo "🔐 Pushing with saved PAT..."
	@echo "🖥️  환경: $(DETECTED_OS)"
	@echo "💡 This feature requires a separate script."
	@echo "Use 'make push-with-pat' for now."
	