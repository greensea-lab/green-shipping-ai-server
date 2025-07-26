# Green Shipping AI Server

🚢 **FastAPI 기반의 백엔드 서버 프로젝트**

Green Shipping AI Server는 **초보 개발자를 위한 완벽한 FastAPI 백엔드 개발 환경**을 제공합니다.

## 🌟 주요 특징

- ✅ **초보자 친화적**: 개발 경험이 없어도 따라할 수 있는 상세한 가이드
- ✅ **완전 자동화**: 한 번의 명령어로 모든 환경 설정 완료
- ✅ **크로스 플랫폼**: macOS, Windows, Linux 모두 지원
- ✅ **실제 동작 예시**: User, Product API가 실제로 작동
- ✅ **테스트 환경**: SQLite를 사용한 즉시 테스트 가능

## 🎯 이 가이드는 누구를 위한 것인가요?

- 프로그래밍 경험이 전혀 없는 분
- Python을 처음 접하는 분
- 웹 개발을 처음 시작하는 분
- Green Shipping AI 프로젝트에 참여하고 싶은 분

## 📋 사전 준비사항

### 1. 필요한 프로그램 설치

#### macOS 사용자
```bash
# Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python
```

#### Windows 사용자
1. **Python 설치**
   - [Python 공식 사이트](https://www.python.org/downloads/)에서 최신 버전 다운로드
   - 설치 시 "Add Python to PATH" 체크박스 반드시 선택

#### Linux 사용자 (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. 설치 확인

```bash
python3 --version
# 또는
python --version
```

## 🚀 1단계: 개발 환경 설정

### 자동화 도구 사용 (권장)

가장 간단한 방법입니다:

```bash
# 1. 저장소 클론
git clone https://github.com/greensea-lab/green-shipping-ai-server.git
cd green-shipping-ai-server

# 2. 개발 환경 자동 설정
make setup

# 3. 로컬 서버 실행
make local

# 4. API 테스트
make test
```

**5분 만에 완전한 FastAPI 백엔드 개발 환경 구축!** 🎯

## 🗄️ 2단계: 환경별 설정

### 환경별 설정 파일

프로젝트는 3가지 환경을 지원합니다:

#### 1. 로컬 환경 (Local) - SQLite 사용
```bash
# 로컬 개발 서버 실행
make local

# 설정 파일: env.local
DATABASE_URL=sqlite:///./local.db
DEBUG=True
```

#### 2. 개발 환경 (Development) - 원격 MySQL 사용
```bash
# 개발 환경 서버 실행
make dev

# 설정 파일: env.dev
DATABASE_URL=mysql+pymysql://dev_user:dev_password@dev-mysql-host:3306/green_shipping_dev
DEBUG=True
```

#### 3. 프로덕션 환경 (Production) - 원격 MySQL 사용
```bash
# 프로덕션 환경 서버 실행 (주의!)
make prod

# 설정 파일: env.production
DATABASE_URL=mysql+pymysql://prod_user:prod_password@prod-mysql-host:3306/green_shipping_prod
DEBUG=False
```

### 환경별 마이그레이션

#### 로컬 환경 (SQLite)
```bash
# 로컬 테스트용 마이그레이션
make migrate
```

#### 개발 환경 (MySQL)
```bash
# 개발 환경 마이그레이션
make migrate-dev
```

#### 프로덕션 환경 (MySQL)
```bash
# 프로덕션 마이그레이션 (보안상 제한됨)
make migrate-prod
```

**⚠️ 주의사항:**
- 프로덕션 마이그레이션은 보안상 로컬에서 실행할 수 없습니다
- 프로덕션 환경에서는 CI/CD 파이프라인이나 서버에서 직접 실행하세요
- 스키마 변경사항이 기존 데이터에 영향을 줄 수 있습니다

## 🚀 3단계: 서버 실행 및 테스트

### 개발 서버 실행

```bash
# 로컬 환경 (SQLite 사용)
make local

# 개발 환경 (원격 MySQL 사용)
make dev

# 프로덕션 환경 (원격 MySQL 사용, 주의!)
make prod
```

성공하면 다음과 같은 메시지가 나타납니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 웹 브라우저에서 확인

웹 브라우저를 열고 다음 주소로 접속해보세요:

- **메인 페이지**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **대체 API 문서 (ReDoc)**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

### API 테스트

```bash
# API 테스트 실행
make test

# 또는 수동으로 테스트
curl http://localhost:8000/api/v1/users/
curl http://localhost:8000/api/v1/products/
```

## 🔐 4단계: GitHub 연동 (선택사항)

### GitHub Personal Access Token (PAT) 설정

#### 1. GitHub에서 PAT 생성

1. **GitHub.com 접속** → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **"Generate new token"** → "Generate new token (classic)" 클릭
3. **토큰 설정**:
   - Note: `green-shipping-ai-server-access`
   - Expiration: 원하는 만료 기간 선택
   - Scopes: `repo` 체크
4. **"Generate token"** 클릭 후 토큰 복사

#### 2. Git 사용자 정보 설정

```bash
# GitHub 사용자 정보 확인
make check-github-user

# GitHub 프로필의 "Name" 필드와 동일하게 설정
git config --global user.name "Your GitHub Profile Name"
git config --global user.email "your.email@example.com"
```

#### 3. PAT 설정 (두 가지 방법)

**방법 1: 한 번만 설정하고 재사용 (권장)**

```bash
# 초기 설정 (한 번만)
make setup-github-pat

# 이후 사용
make push-with-pat-saved
```

**방법 2: 매번 PAT 입력**

```bash
make push-with-pat
```

## 📚 5단계: API 사용법

### 기본 API 엔드포인트

#### 사용자 API

1. **사용자 목록 조회**: GET http://localhost:8000/api/v1/users/
2. **사용자 생성**: POST http://localhost:8000/api/v1/users/
3. **특정 사용자 조회**: GET http://localhost:8000/api/v1/users/{user_id}
4. **사용자 정보 수정**: PUT http://localhost:8000/api/v1/users/{user_id}
5. **사용자 삭제**: DELETE http://localhost:8000/api/v1/users/{user_id}

#### 상품 API

1. **상품 목록 조회**: GET http://localhost:8000/api/v1/products/
2. **상품 생성**: POST http://localhost:8000/api/v1/products/
3. **특정 상품 조회**: GET http://localhost:8000/api/v1/products/{product_id}
4. **상품 정보 수정**: PUT http://localhost:8000/api/v1/products/{product_id}
5. **상품 삭제**: DELETE http://localhost:8000/api/v1/products/{product_id}

### API 테스트 방법

#### 1. 웹 브라우저에서 테스트
- http://localhost:8000/docs 접속
- "Try it out" 버튼 클릭
- 파라미터 입력 후 "Execute" 클릭

#### 2. curl 명령어로 테스트
```bash
# 사용자 생성
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'

# 상품 생성
curl -X POST "http://localhost:8000/api/v1/products/" \
     -H "Content-Type: application/json" \
     -d '{"name": "샘플 상품", "description": "샘플 설명", "price": 10000, "stock_quantity": 50}'

# 상품 목록 조회
curl http://localhost:8000/api/v1/products/
```

## 🛠️ 6단계: 개발 가이드

### 자동화 도구 사용법

#### Makefile 명령어
```bash
# 📋 기본 명령어
make help          # 사용 가능한 명령어 확인
make setup         # 개발 환경 초기 설정
make local         # 로컬 개발 서버 실행 (SQLite)
make dev           # 개발 환경 서버 실행 (원격 MySQL)
make prod          # 프로덕션 환경 서버 실행 (원격 MySQL)
make test          # API 테스트
make status        # 서버 상태 확인
make clean         # 가상환경 삭제

# 🗄️  데이터베이스
make migrate                          # 로컬 마이그레이션 적용 (SQLite)
make migrate-dev                      # 개발 환경 마이그레이션 적용 (MySQL)
make migrate-prod                     # 프로덕션 마이그레이션 (보안상 제한)
make migrate-create MESSAGE='설명'    # 새 마이그레이션 생성

# 🔐 GitHub Push
make push-with-pat                    # PAT를 사용하여 GitHub에 Push
make push-with-pat-saved              # 저장된 PAT를 사용하여 Push
make setup-github-pat                 # GitHub PAT 초기 설정
make check-github-user                # GitHub 사용자 정보 확인
make check-env                        # 환경별 설정 확인
```

### 새로운 기능 추가하기

#### 1. 새로운 모델 추가
```bash
# app/models/your_model.py 생성
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### 2. Pydantic 스키마 추가
```bash
# app/schemas/your_schema.py 생성
from pydantic import BaseModel
from datetime import datetime

class YourModelBase(BaseModel):
    name: str

class YourModelCreate(YourModelBase):
    pass

class YourModel(YourModelBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 3. API 엔드포인트 추가
```bash
# app/api/v1/endpoints/your_endpoints.py 생성
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.your_schema import YourModel, YourModelCreate
from app.models.your_model import YourModel as YourModelDB

router = APIRouter()

@router.get("/", response_model=List[YourModel])
def get_items(db: Session = Depends(get_db)):
    return db.query(YourModelDB).all()

@router.post("/", response_model=YourModel)
def create_item(item: YourModelCreate, db: Session = Depends(get_db)):
    db_item = YourModelDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
```

#### 4. 라우터 등록
```bash
# app/api/v1/api.py에 추가:
from app.api.v1.endpoints import your_endpoints

api_router.include_router(your_endpoints.router, prefix="/your-items", tags=["your-items"])
```

#### 5. 데이터베이스 마이그레이션
```bash
# 새 마이그레이션 생성
make migrate-create MESSAGE="Add your model"

# 로컬 테스트용 마이그레이션
make migrate

# 개발 환경 마이그레이션
make migrate-dev

# 프로덕션 환경 마이그레이션 (보안상 제한됨)
make migrate-prod
```

### 의존성 관리

#### 🚀 가장 간단한 방법 (권장)

**requirements.txt에 패키지를 추가한 후:**

```bash
make install-deps
```

#### 📝 수동으로 패키지 추가

```bash
# 가상환경 활성화 후 pip 사용
source venv/bin/activate
pip install package_name
pip freeze > requirements.txt
```

#### 📦 의존성 관리 명령어

```bash
make install-deps    # requirements.txt에서 패키지 설치
```

## 📁 프로젝트 구조

```
green-shipping-ai-server/
├── 📁 app/                    # 메인 애플리케이션
│   ├── 📁 api/v1/endpoints/   # API 엔드포인트들
│   ├── 📁 models/             # 데이터베이스 모델들
│   └── 📁 schemas/            # 데이터 검증 스키마들
├── 📁 alembic/                # 데이터베이스 마이그레이션
├── 📄 requirements.txt        # Python 의존성 목록
├── 📄 .env                    # 환경 변수 설정
├── 📄 Makefile                # 자동화 도구
└── 📄 README.md               # 이 파일
```

**주요 개발 패키지:**
- `app/models/`: 데이터베이스 테이블 구조 정의
- `app/schemas/`: API 요청/응답 데이터 검증
- `app/api/v1/endpoints/`: 실제 API 기능 구현

## 🔧 문제 해결

### 자주 발생하는 문제들

#### 1. "command not found: python3"
- Python이 설치되지 않았거나 PATH에 추가되지 않았습니다
- Python 설치를 다시 확인해주세요

#### 2. "pip: command not found"
- 가상환경이 활성화되지 않았습니다
- `make setup`을 다시 실행해주세요

#### 3. "Access denied for user"
- 원격 MySQL 데이터베이스 접근 권한이 없습니다
- 환경별 설정 파일(env.dev, env.production)의 데이터베이스 연결 정보를 확인해주세요

#### 4. "ModuleNotFoundError"
- 필요한 라이브러리가 설치되지 않았습니다
- `make install-deps`를 다시 실행해주세요

#### 5. "Connection refused" (데이터베이스)
- 원격 MySQL 서버에 연결할 수 없습니다
- 네트워크 연결 및 환경별 설정 파일을 확인해주세요
- env.dev 또는 env.production 파일의 DATABASE_URL을 확인하세요

#### 6. 서버가 시작되지 않음
- 포트 8000이 이미 사용 중일 수 있습니다
- 다른 포트로 실행: `uvicorn app.main:app --reload --port 8001`

#### 7. "Authentication failed" (GitHub Push)
- PAT가 잘못되었거나 만료됨
- GitHub에서 새 토큰 생성 후 다시 설정

## 🆘 도움이 필요하시다면

1. **에러 메시지를 복사해서 검색해보세요**
   - Google, Stack Overflow에서 비슷한 문제를 찾을 수 있습니다

2. **단계별로 다시 확인해보세요**
   - 각 단계가 성공했는지 확인하고 다음 단계로 진행하세요

3. **터미널 메시지를 주의깊게 읽어보세요**
   - 에러 메시지에 해결 방법이 포함되어 있을 수 있습니다

## 🎉 축하합니다!

이제 Green Shipping AI Server 개발 환경이 완성되었습니다!
서버가 정상적으로 실행되고 있다면, 웹 개발의 첫 걸음을 내딛은 것입니다.

앞으로 새로운 기능을 추가하거나 문제가 생기면 언제든 이 README를 참고하세요. 