# Green Shipping AI Server

🚢 **FastAPI 기반의 백엔드 서버 프로젝트**

Green Shipping AI Server는 **초보 개발자를 위한 완벽한 FastAPI 백엔드 개발 환경**을 제공합니다.

## 🌟 주요 특징

- ✅ **초보자 친화적**: 개발 경험이 없어도 따라할 수 있는 상세한 가이드
- ✅ **완전 자동화**: 한 번의 명령어로 모든 환경 설정 완료
- ✅ **크로스 플랫폼**: macOS, Windows, Linux 모두 지원
- ✅ **실제 동작 예시**: User, Product API가 실제로 작동
- ✅ **테스트 환경**: SQLite를 사용한 즉시 테스트 가능

## 🚀 빠른 시작

```bash
# 1. 저장소 클론
git clone https://github.com/greensea-lab/green-shipping-ai-server.git
cd green-shipping-ai-server

# 2. 개발 환경 설정 (한 번만)
make setup

# 3. 테스트 서버 실행
make dev-test

# 4. API 테스트
make test
```

**5분 만에 완전한 FastAPI 백엔드 개발 환경 구축!** 🎯

## 🎯 이 가이드는 누구를 위한 것인가요?

- 프로그래밍 경험이 전혀 없는 분
- Python을 처음 접하는 분
- 웹 개발을 처음 시작하는 분
- Green Shipping AI 프로젝트에 참여하고 싶은 분

## 📋 사전 준비사항

### 1. 필요한 프로그램 설치

#### macOS 사용자
1. **Homebrew 설치** (터미널에서 실행)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Python 설치**
   ```bash
   brew install python
   ```

3. **MySQL 설치**
   ```bash
   brew install mysql
   ```

#### Windows 사용자
1. **Python 설치**
   - [Python 공식 사이트](https://www.python.org/downloads/)에서 최신 버전 다운로드
   - 설치 시 "Add Python to PATH" 체크박스 반드시 선택

2. **MySQL 설치**
   - [MySQL 공식 사이트](https://dev.mysql.com/downloads/mysql/)에서 다운로드
   - 또는 [XAMPP](https://www.apachefriends.org/) 설치 (MySQL 포함)

#### Linux 사용자 (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server
```

### 2. 설치 확인

터미널(명령 프롬프트)을 열고 다음 명령어를 실행해보세요:

```bash
python3 --version
# 또는
python --version
```

버전 정보가 나오면 설치가 완료된 것입니다.

## 🚀 빠른 시작 (자동화 도구 사용)

### 방법 1: Makefile 사용 (추천)

가장 간단한 방법입니다:

```bash
# 1. 개발 환경 자동 설정
make setup

# 2. 서버 실행
make dev

# 3. API 테스트
make test
```

### 방법 2: 의존성 추가 후 설치

requirements.txt에 패키지를 추가한 후:

```bash
# macOS/Linux
./install_deps.sh

# Windows
.\install_deps.ps1

# 또는
make install-deps
```

### 방법 2: 스크립트 사용

#### macOS/Linux 사용자:
```bash
# 1. 스크립트 실행 권한 부여
chmod +x setup_dev.sh

# 2. 개발 환경 설정
./setup_dev.sh

# 3. 서버 실행
./dev.sh
```

#### Windows 사용자:
```powershell
# 1. PowerShell에서 실행 정책 변경 (관리자 권한 필요)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. 개발 환경 설정
.\setup_dev.ps1

# 3. 서버 실행
.\dev.ps1
```

## 📋 수동 설치 가이드

자동화 도구가 작동하지 않는 경우 다음 단계를 따라하세요:

### 1단계: 프로젝트 폴더로 이동

터미널을 열고 프로젝트 폴더로 이동합니다:

```bash
cd /Users/jiyoung/PycharmProjects/green-shipping-ai-server
```

### 2단계: Python 가상환경 생성

가상환경은 프로젝트별로 독립적인 Python 환경을 만들어주는 도구입니다.

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (매번 실행해야 함)
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

성공하면 터미널 앞에 `(venv)`가 표시됩니다.

### 3단계: 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

이 과정은 몇 분 정도 걸릴 수 있습니다.

### 4단계: MySQL 데이터베이스 설정

#### MySQL 서버 시작

**macOS:**
```bash
brew services start mysql
```

**Windows:**
- MySQL이 설치된 경우 자동으로 시작됩니다
- XAMPP를 사용하는 경우 XAMPP Control Panel에서 MySQL 시작

**Linux:**
```bash
sudo systemctl start mysql
```

#### MySQL 접속 및 데이터베이스 생성

```bash
# MySQL에 접속 (처음에는 비밀번호가 없을 수 있음)
mysql -u root -p

# MySQL 프롬프트에서 실행:
CREATE DATABASE green_shipping_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'green_user'@'localhost' IDENTIFIED BY 'green_password';
GRANT ALL PRIVILEGES ON green_shipping_db.* TO 'green_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5단계: 환경 변수 설정

프로젝트 폴더에서 `.env` 파일을 생성하고 편집합니다:

```bash
# macOS/Linux:
cp env.example .env
nano .env

# Windows:
# copy env.example .env
# notepad .env
```

`.env` 파일의 내용을 다음과 같이 수정하세요:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://green_user:green_password@localhost:3306/green_shipping_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=green_user
MYSQL_PASSWORD=green_password
MYSQL_DATABASE=green_shipping_db
```

### 6단계: 데이터베이스 테이블 생성

#### 옵션 A: MySQL 사용 (권장)
```bash
# 가상환경이 활성화되어 있는지 확인 (터미널 앞에 (venv) 표시)
# 활성화되어 있지 않다면:
source venv/bin/activate

# 데이터베이스 테이블 생성
alembic upgrade head
```

#### 옵션 B: SQLite 사용 (빠른 테스트용)
MySQL 설정이 복잡하다면 SQLite로 빠르게 테스트할 수 있습니다:

1. **테스트 서버 실행**
   ```bash
   make dev-test
   ```

2. **API 테스트**
   ```bash
   make test
   ```

3. **수동으로 SQLite 설정**
   ```bash
   # .env 파일에서 DATABASE_URL을 SQLite로 변경
   DATABASE_URL=sqlite:///./test.db
   
   # 서버 실행
   make dev
   ```

### 7단계: 서버 실행

```bash
# 개발 모드로 서버 실행
uvicorn app.main:app --reload
```

성공하면 다음과 같은 메시지가 나타납니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 8단계: 웹 브라우저에서 확인

웹 브라우저를 열고 다음 주소로 접속해보세요:

- **메인 페이지**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **대체 API 문서 (ReDoc)**: http://localhost:8000/redoc

## 🔧 문제 해결

### 자주 발생하는 문제들

#### 1. "command not found: python3"
- Python이 설치되지 않았거나 PATH에 추가되지 않았습니다
- Python 설치를 다시 확인해주세요

#### 2. "pip: command not found"
- 가상환경이 활성화되지 않았습니다
- `source venv/bin/activate` 명령어를 실행해주세요

#### 3. "Access denied for user"
- MySQL 사용자 생성이 제대로 되지 않았습니다
- MySQL에서 사용자 생성 과정을 다시 확인해주세요

#### 4. "ModuleNotFoundError"
- 필요한 라이브러리가 설치되지 않았습니다
- `pip install -r requirements.txt`를 다시 실행해주세요

#### 5. 서버가 시작되지 않음
- 포트 8000이 이미 사용 중일 수 있습니다
- 다른 포트로 실행: `uvicorn app.main:app --reload --port 8001`

## 📚 API 사용법

### 기본 API 엔드포인트

1. **사용자 목록 조회**
   - GET http://localhost:8000/api/v1/users/

2. **사용자 생성**
   - POST http://localhost:8000/api/v1/users/
   - Body: `{"email": "test@example.com", "username": "testuser", "password": "password123"}`

3. **특정 사용자 조회**
   - GET http://localhost:8000/api/v1/users/{user_id}

4. **사용자 정보 수정**
   - PUT http://localhost:8000/api/v1/users/{user_id}

5. **사용자 삭제**
   - DELETE http://localhost:8000/api/v1/users/{user_id}

### 상품 API 엔드포인트 (예시)

1. **상품 목록 조회**
   - GET http://localhost:8000/api/v1/products/

2. **상품 생성**
   - POST http://localhost:8000/api/v1/products/
   - Body: `{"name": "샘플 상품", "description": "샘플 설명", "price": 10000, "stock_quantity": 50}`

3. **특정 상품 조회**
   - GET http://localhost:8000/api/v1/products/{product_id}

4. **상품 정보 수정**
   - PUT http://localhost:8000/api/v1/products/{product_id}
   - Body: `{"price": 15000}` (수정할 필드만 전송)

5. **상품 삭제 (비활성화)**
   - DELETE http://localhost:8000/api/v1/products/{product_id}

### API 테스트 방법

1. **웹 브라우저에서 테스트**
   - http://localhost:8000/docs 접속
   - "Try it out" 버튼 클릭
   - 파라미터 입력 후 "Execute" 클릭

2. **curl 명령어로 테스트**
   ```bash
   # 사용자 생성
   curl -X POST "http://localhost:8000/api/v1/users/" \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'
   
   # 상품 생성 (예시)
   curl -X POST "http://localhost:8000/api/v1/products/" \
        -H "Content-Type: application/json" \
        -d '{"name": "샘플 상품", "description": "샘플 설명", "price": 10000, "stock_quantity": 50}'
   
   # 상품 목록 조회
   curl http://localhost:8000/api/v1/products/
   
   # 상품 수정
   curl -X PUT "http://localhost:8000/api/v1/products/1" \
        -H "Content-Type: application/json" \
        -d '{"price": 15000}'
   ```

## 🛠️ 개발 가이드

### 자동화 도구 사용법

#### Makefile 명령어
```bash
# 📋 기본 명령어
make help          # 사용 가능한 명령어 확인
make setup         # 개발 환경 초기 설정
make dev           # 개발 서버 실행 (MySQL)
make dev-test      # 테스트 서버 실행 (SQLite)
make test          # API 테스트
make status        # 서버 상태 확인
make clean         # 가상환경 삭제

# 📦 의존성 관리
make install-package PACKAGE=name     # 새 패키지 설치
make install-dev-package PACKAGE=name # 개발용 패키지 설치
make uninstall-package PACKAGE=name   # 패키지 제거
make update-deps                      # 의존성 업데이트

# 🗄️  데이터베이스
make migrate                          # 마이그레이션 적용
make migrate-create MESSAGE='설명'    # 새 마이그레이션 생성

# 🎨 코드 품질
make format                           # 코드 포맷팅
make lint                             # 코드 품질 검사
make test-run                         # 테스트 실행
```

#### 스크립트 사용법
```bash
# macOS/Linux
./setup_dev.sh     # 개발 환경 설정
./dev.sh           # 서버 실행
./test_api.sh      # API 테스트

# Windows
.\setup_dev.ps1    # 개발 환경 설정
.\dev.ps1          # 서버 실행
.\test_api.ps1     # API 테스트
```

### 새로운 기능 추가하기

#### 1. 새로운 모델 추가
```bash
# 1. 모델 파일 생성
# app/models/product.py 예시:
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### 2. Pydantic 스키마 추가
```bash
# app/schemas/product.py 예시:
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 3. API 엔드포인트 추가
```bash
# app/api/v1/endpoints/products.py 예시:
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.product import Product, ProductCreate
from app.models.product import Product as ProductModel

router = APIRouter()

@router.get("/", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductModel).all()

@router.post("/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
```

#### 4. 라우터 등록
```bash
# app/api/v1/api.py에 추가:
from app.api.v1.endpoints import products

api_router.include_router(products.router, prefix="/products", tags=["products"])
```

#### 5. 데이터베이스 마이그레이션
```bash
# 자동화 도구 사용
make migrate-create MESSAGE="Add product model"
make migrate

# 또는 수동으로
alembic revision --autogenerate -m "Add product model"
alembic upgrade head
```

### 의존성 관리

#### 🚀 가장 간단한 방법 (권장)

**requirements.txt에 패키지를 추가한 후:**

```bash
# macOS/Linux
./install_deps.sh

# Windows
.\install_deps.ps1

# 또는 Makefile 사용
make install-deps
```

#### 📝 수동으로 패키지 추가

```bash
# 1. 가상환경 활성화
./activate_venv.sh

# 2. 패키지 설치
pip install package_name

# 3. requirements.txt 업데이트
pip freeze > requirements.txt

# 4. 다른 개발자들과 공유
git add requirements.txt
git commit -m "Add new dependency: package_name"
```

#### 🔧 자동화 도구 사용

```bash
# 새 패키지 설치 (자동으로 requirements.txt 업데이트)
make install-package PACKAGE=package_name

# 개발용 패키지 설치
make install-dev-package PACKAGE=pytest

# 패키지 제거
make uninstall-package PACKAGE=package_name

# 특정 버전 설치
pip install package_name==1.2.3
pip freeze > requirements.txt
```

#### 💡 의존성 관리 팁

1. **requirements.txt 수정 후**
   ```bash
   ./install_deps.sh  # 자동 설치
   ```

2. **문제 발생 시 복원**
   ```bash
   pip install -r requirements_backup.txt
   ```

3. **패키지 목록 확인**
   ```bash
   pip list
   ```

4. **의존성 업데이트**
   ```bash
   make update-deps
   ```

### 코드 수정 후 서버 재시작

개발 모드에서는 코드를 수정하면 자동으로 서버가 재시작됩니다.
만약 자동 재시작이 안 된다면:

```bash
# 자동화 도구 사용
make dev

# 또는 수동으로
uvicorn app.main:app --reload
```

### 개발 워크플로우

#### 1. 새로운 기능 개발
```bash
# 1. 가상환경 활성화
./activate_venv.sh

# 2. 서버 실행
make dev

# 3. 새 터미널에서 API 테스트
make test
```

#### 2. 코드 품질 관리
```bash
# 코드 포맷팅
black app/

# 린팅 (코드 품질 검사)
flake8 app/

# 타입 체크 (mypy 설치 후)
mypy app/
```

#### 3. 테스트 작성
```bash
# 테스트 파일 생성: tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "username": "testuser", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

# 테스트 실행
pytest tests/
```

### IDE 설정

#### VS Code
- 프로젝트를 열면 자동으로 가상환경이 인식됩니다
- F5 키로 디버깅 실행 가능
- Python 확장 프로그램 설치 권장
- **터미널에서 가상환경 활성화:**
  ```bash
  ./activate_venv.sh
  ```

#### PyCharm
- 프로젝트를 열고 Python 인터프리터를 `venv/bin/python`으로 설정
- Run Configuration에서 "FastAPI" 설정 사용 가능
- **터미널에서 가상환경 활성화:**
  ```bash
  ./activate_venv.sh
  ```

### IDE 터미널에서 가상환경 활성화

IDE 터미널에서 가상환경이 활성화되지 않은 경우:

#### macOS/Linux:
```bash
# 방법 1: 스크립트 사용 (권장)
./activate_venv.sh

# 방법 2: 수동 활성화
source venv/bin/activate

# 방법 3: Makefile 사용
make activate-ide
```

#### Windows:
```powershell
# 방법 1: 스크립트 사용 (권장)
.\activate_venv.ps1

# 방법 2: 수동 활성화
venv\Scripts\Activate.ps1
```

#### 가상환경 확인:
```bash
# 가상환경이 활성화되었는지 확인
echo $VIRTUAL_ENV  # macOS/Linux
echo $env:VIRTUAL_ENV  # Windows PowerShell

# Python 경로 확인
which python  # macOS/Linux
Get-Command python  # Windows PowerShell
```

## 📁 프로젝트 구조 상세 가이드

### 🗂️ 전체 디렉토리 구조

```
green-shipping-ai-server/
├── 📁 app/                           # 메인 애플리케이션 폴더
│   ├── 📄 main.py                    # 서버 시작점 (수정하지 않음)
│   ├── 📄 config.py                  # 설정 관리 (수정하지 않음)
│   ├── 📄 database.py                # 데이터베이스 연결 (수정하지 않음)
│   ├── 📁 api/                       # API 관련 파일들
│   │   └── 📁 v1/                    # API 버전 1
│   │       ├── 📄 api.py             # API 라우터 설정 (여기에 새 라우터 추가)
│   │       └── 📁 endpoints/         # API 엔드포인트들 (여기에 새 API 추가)
│   │           └── 📄 users.py       # 사용자 API 예시
│   ├── 📁 models/                    # 데이터베이스 모델들 (여기에 새 모델 추가)
│   │   └── 📄 user.py                # 사용자 모델 예시
│   └── 📁 schemas/                   # 데이터 검증 스키마들 (여기에 새 스키마 추가)
│       └── 📄 user.py                # 사용자 스키마 예시
├── 📁 alembic/                       # 데이터베이스 마이그레이션 (자동 생성)
├── 📁 .vscode/                       # VS Code 설정 파일들 (자동 생성)
├── 📁 venv/                          # Python 가상환경 (자동 생성)
├── 📄 requirements.txt               # 필요한 Python 라이브러리 목록 (여기에 패키지 추가)
├── 📄 .env                           # 환경 변수 (개인 설정)
├── 📄 Makefile                       # 자동화 도구 (make 명령어)
├── 📄 setup_dev.sh                   # 개발 환경 설정 스크립트 (macOS/Linux)
├── 📄 setup_dev.ps1                  # 개발 환경 설정 스크립트 (Windows)
├── 📄 dev.sh                         # 서버 실행 스크립트 (macOS/Linux)
├── 📄 dev.ps1                        # 서버 실행 스크립트 (Windows)
├── 📄 test_api.sh                    # API 테스트 스크립트 (macOS/Linux)
├── 📄 test_api.ps1                   # API 테스트 스크립트 (Windows)
├── 📄 install_deps.sh                # 의존성 설치 스크립트 (macOS/Linux)
├── 📄 install_deps.ps1               # 의존성 설치 스크립트 (Windows)
├── 📄 activate_venv.sh               # 가상환경 활성화 스크립트 (macOS/Linux)
├── 📄 activate_venv.ps1              # 가상환경 활성화 스크립트 (Windows)
└── 📄 README.md                      # 이 파일
```

### 📝 파일 작성 위치 가이드

#### 🆕 새로운 기능 추가 시 작성할 파일들

**1. 데이터베이스 모델 (필수)**
```
📁 app/models/
└── 📄 your_model.py    # 새로 생성
```
- **용도**: 데이터베이스 테이블 구조 정의
- **예시**: `app/models/product.py`, `app/models/order.py`

**2. 데이터 검증 스키마 (필수)**
```
📁 app/schemas/
└── 📄 your_schema.py   # 새로 생성
```
- **용도**: API 요청/응답 데이터 검증
- **예시**: `app/schemas/product.py`, `app/schemas/order.py`

**3. API 엔드포인트 (필수)**
```
📁 app/api/v1/endpoints/
└── 📄 your_endpoints.py # 새로 생성
```
- **용도**: 실제 API 기능 구현
- **예시**: `app/api/v1/endpoints/products.py`

**4. 라우터 등록 (필수)**
```
📄 app/api/v1/api.py   # 기존 파일 수정
```
- **용도**: 새 API를 서버에 등록

#### 🔧 설정 파일들 (수정하지 않음)

**자동 생성되는 파일들:**
- `app/main.py` - 서버 시작점
- `app/config.py` - 설정 관리
- `app/database.py` - 데이터베이스 연결
- `alembic/` - 마이그레이션 파일들
- `.vscode/` - IDE 설정

**개발자가 수정하는 파일들:**
- `requirements.txt` - 패키지 추가
- `.env` - 환경 변수 설정

### 🚀 새로운 기능 추가 워크플로우

#### 예시: "상품(Product)" 기능 추가

**1단계: 모델 생성**
```bash
# 파일 위치: app/models/product.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**2단계: 스키마 생성**
```bash
# 파일 위치: app/schemas/product.py
from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    price: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**3단계: API 엔드포인트 생성**
```bash
# 파일 위치: app/api/v1/endpoints/products.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product import Product, ProductCreate
from app.models.product import Product as ProductModel

router = APIRouter()

@router.get("/", response_model=List[Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductModel).all()

@router.post("/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
```

**4단계: 라우터 등록**
```bash
# 파일 위치: app/api/v1/api.py (기존 파일 수정)
from app.api.v1.endpoints import products

api_router.include_router(products.router, prefix="/products", tags=["products"])
```

**5단계: 데이터베이스 마이그레이션**
```bash
make migrate-create MESSAGE="Add product model"
make migrate
```

### 📋 파일별 역할 설명

#### 🔧 핵심 파일들 (수정하지 않음)
- **`app/main.py`**: FastAPI 서버 시작점
- **`app/config.py`**: 데이터베이스 연결 정보, 보안 설정
- **`app/database.py`**: SQLAlchemy 데이터베이스 연결 설정

#### ✏️ 개발자가 작성하는 파일들
- **`app/models/`**: 데이터베이스 테이블 구조 (SQLAlchemy)
- **`app/schemas/`**: API 데이터 검증 (Pydantic)
- **`app/api/v1/endpoints/`**: 실제 API 기능 구현
- **`app/api/v1/api.py`**: API 라우터 등록

#### ⚙️ 설정 파일들
- **`requirements.txt`**: Python 패키지 목록
- **`.env`**: 데이터베이스 비밀번호, API 키 등
- **`alembic/`**: 데이터베이스 마이그레이션 (자동 생성)

### 💡 초보자를 위한 팁

1. **새로운 기능 추가 시 순서:**
   - 모델 → 스키마 → API → 라우터 등록 → 마이그레이션

2. **파일명 규칙:**
   - 모델: `app/models/table_name.py`
   - 스키마: `app/schemas/table_name.py`
   - API: `app/api/v1/endpoints/table_name.py`

3. **클래스명 규칙:**
   - 모델: `Product` (단수형, 대문자)
   - 스키마: `Product`, `ProductCreate`, `ProductUpdate`

4. **API 경로 규칙:**
   - 목록 조회: `GET /api/v1/products/`
   - 상세 조회: `GET /api/v1/products/{id}`
   - 생성: `POST /api/v1/products/`
   - 수정: `PUT /api/v1/products/{id}`
   - 삭제: `DELETE /api/v1/products/{id}`

### ⚠️ 주의사항

1. **MySQL 연결 오류가 발생하는 경우:**
   - MySQL 서버가 실행되지 않았거나 설정이 잘못된 경우입니다
   - `make dev-test` 명령어로 SQLite를 사용한 테스트 서버를 실행할 수 있습니다
   - 실제 데이터베이스 연결은 MySQL 설정 후에 가능합니다

2. **서버 시작 시 오류가 발생하는 경우:**
   - `make dev-test`로 SQLite 테스트 서버를 실행하세요
   - 또는 데이터베이스 연결 없이 테스트하려면 `app/main.py`의 `Base.metadata.create_all(bind=engine)` 라인을 주석 처리하세요

### 🧪 테스트 데이터베이스 설정

#### SQLite 테스트 서버 사용법

1. **테스트 서버 실행**
   ```bash
   make dev-test
   ```

2. **테스트 데이터 추가 (선택사항)**
   ```bash
   # 사용자 테스트 데이터 추가
   sqlite3 test.db "INSERT INTO users (email, username, hashed_password, is_active, is_superuser, created_at, updated_at) VALUES ('test@example.com', 'testuser', 'password123', 1, 0, datetime('now'), datetime('now'));"
   
   # 상품 테스트 데이터 추가
   sqlite3 test.db "INSERT INTO products (name, description, price, stock_quantity, is_active, created_at, updated_at) VALUES ('샘플 상품', '샘플 상품 설명입니다.', 10000, 50, 1, datetime('now'), datetime('now'));"
   ```

3. **API 테스트**
   ```bash
   # 사용자 API 테스트
   curl http://localhost:8000/api/v1/users/
   
   # 상품 API 테스트
   curl http://localhost:8000/api/v1/products/
   ```

4. **웹 브라우저에서 확인**
   - API 문서: http://localhost:8000/docs
   - 메인 페이지: http://localhost:8000/
   - 헬스 체크: http://localhost:8000/health

### 📚 실제 예시 파일들

프로젝트에는 "상품(Product)" 기능이 예시로 구현되어 있습니다:

- **모델**: `app/models/product.py` - 데이터베이스 테이블 구조
- **스키마**: `app/schemas/product.py` - API 데이터 검증
- **API**: `app/api/v1/endpoints/products.py` - 실제 API 기능
- **라우터**: `app/api/v1/api.py` - API 등록

이 파일들을 참고하여 새로운 기능을 추가하세요!

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