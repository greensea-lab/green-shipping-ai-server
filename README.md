feat/ai
# Green Shipping AI Server

🚢 **FastAPI 기반의 백엔드 서버 프로젝트**

초보 개발자를 위한 완벽한 FastAPI 백엔드 개발 환경을 제공합니다.

## 🚀 빠른 시작 (10분 완성)

### 1단계: 필수 프로그램 설치

#### macOS 사용자
```bash
# Homebrew 설치 (이미 설치되어 있다면 건너뛰기)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3.11과 Make 설치
brew install python@3.11 make

# 설치 확인
python --version    # Python 3.11.x 출력되어야 함
make --version      # GNU Make 출력되어야 함
```

#### Windows 사용자
1. **Python 3.11 설치**
   - [Python 3.11.8 다운로드](https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe)
   - ⚠️ **중요**: 설치 시 "Add Python to PATH" 체크박스 반드시 선택
   - 설치 후 **반드시 새 터미널 열기**

2. **Git for Windows 설치**
   - [Git for Windows 다운로드](https://git-scm.com/download/win)
   - 기본 설정으로 설치 (Git Bash 포함)

3. **설치 확인**
   ```bash
   # Git Bash에서 실행 (PowerShell/CMD가 아닌 Git Bash 필수)
   python --version    # Python 3.11.x 출력되어야 함
   make --version      # GNU Make 출력되어야 함
   ```

### 2단계: 프로젝트 받기

#### 방법 1: PyCharm에서 Clone (권장)
1. PyCharm 실행
2. **시작 화면에서 "Get from VCS"** 클릭 
   - 💡 시작 화면이 안 보이면: File → New → Project from Version Control
3. **Repository URL** 입력: `https://github.com/greensea-lab/green-shipping-ai-server.git`
4. **Directory** 선택: 
   ```
   Windows: C:\Users\[사용자명]\Desktop\green-shipping-ai-server
   macOS: /Users/[사용자명]/Desktop/green-shipping-ai-server
   ```
5. **Clone** 클릭 (⏱️ 약 30초-1분 소요)
6. **Trust Project** 클릭

**✅ 성공 확인:** PyCharm에서 프로젝트 파일들이 왼쪽 탐색기에 표시됨

#### 방법 2: 터미널에서 Clone
```bash
# 원하는 폴더에서 실행
git clone https://github.com/greensea-lab/green-shipping-ai-server.git
cd green-shipping-ai-server

# 현재 경로 확인 (green-shipping-ai-server 폴더 안에 있어야 함)
pwd
```

### 3단계: 개발 환경 설정 및 서버 실행

#### PyCharm 사용자 (권장)

**1. PyCharm 터미널 열기**
- PyCharm 화면 **하단**에 있는 **"Terminal"** 탭 클릭
- 💡 Terminal 탭이 안 보이면: View → Tool Windows → Terminal
- **✅ 확인사항:** 터미널에 프로젝트 경로(`green-shipping-ai-server`)가 표시되는지 확인

**2. 명령어 순서대로 실행**

**첫 번째: 개발 환경 설정**
```bash
make setup
```
- ⏱️ **소요 시간:** 3-5분 (가상환경 생성 + 패키지 설치)
- 📋 **진행 상황:** 
  ```
  Creating virtual environment...
  Installing dependencies...
  Successfully installed xxx packages
  ```
- **✅ 성공 확인:** "Setup completed successfully!" 메시지 표시

**두 번째: 서버 실행**
```bash
make local
```
- ⏱️ **소요 시간:** 10-30초
- 📋 **성공 메시지:**
  ```
  INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
  INFO:     Started reloader process
  ```
- **✅ 성공 확인:** 브라우저가 자동으로 열리거나, 위 메시지가 나타남

**⚠️ 중요:** 서버가 실행되면 터미널이 "대기 상태"가 됩니다. 이것은 정상입니다!

#### 터미널 사용자
```bash
# 1. 프로젝트 폴더 안에 있는지 확인
pwd  # 경로 끝에 green-shipping-ai-server가 있어야 함

# 2. 개발 환경 설정 (첫 실행시에만)
make setup

# 3. 서버 실행
make local
```

### 4단계: 실행 확인

#### 1. 웹 브라우저에서 확인

**수동으로 접속:**
1. 웹 브라우저 열기 (Chrome, Firefox, Safari 등)
2. 주소창에 입력: `http://localhost:8000`
3. Enter 키 누르기

**✅ 성공 확인:**
- 웹페이지가 정상적으로 로드됨
- API 문서 확인: http://localhost:8000/docs

#### 2. API 테스트 (새 터미널에서)

**PyCharm 사용자:**
1. **새 터미널 탭 열기:** Terminal 탭 옆의 **"+"** 버튼 클릭
2. **테스트 실행:**
   ```bash
   make test
   ```

**외부 터미널 사용자:**
1. **새 터미널 창 열기** (기존 터미널은 서버 실행 중이므로 건드리지 않음)
2. **프로젝트 폴더로 이동:**
   ```bash
   cd green-shipping-ai-server
   ```
3. **테스트 실행:**
   ```bash
   make test
   ```

**✅ 테스트 성공 확인:**
```
Testing API endpoints...
✓ Health check: OK
✓ API documentation: OK
All tests passed!
```

#### 3. 서버 종료 방법

**서버를 중단하고 싶을 때:**
- 서버가 실행 중인 터미널에서 `Ctrl+C` 누르기 (Mac: `Cmd+C`)
- **✅ 종료 확인:** 터미널이 다시 명령어 입력 대기 상태로 돌아감

## ⚠️ 문제 해결

### 자주 발생하는 문제들

#### 1. "Python 3.11.x가 설치되지 않았습니다"

**macOS 해결법:**
```bash
# Python 3.11 설치
brew install python@3.11

# 새 터미널 열고 확인
python --version  # Python 3.11.x 출력되어야 함

# 💡 Homebrew 설치 시 자동으로 PATH에 추가됨
# 별도의 PATH 설정 불필요!
```

**Windows 해결법:**
1. **Python 재설치 (가장 확실한 방법)**
   - 기존 Python 제거: Windows 키 + R → `appwiz.cpl` → Python 제거
   - [Python 3.11.8 다운로드](https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe)
   - **"Add Python to PATH"** 반드시 체크 ✅
   - 설치 후 **컴퓨터 재시작**

2. **PATH 수동 추가 (설치 시 체크하지 않은 경우)**
   
   **방법 1: 시스템 환경변수에서 추가**
   - Windows 키 + R → `sysdm.cpl` → 고급 → 환경 변수
   - **시스템 변수**에서 **Path** 선택 → **편집** 클릭
   - **새로 만들기**로 다음 경로들 추가:
     ```
     C:\Users\[사용자명]\AppData\Local\Programs\Python\Python311\
     C:\Users\[사용자명]\AppData\Local\Programs\Python\Python311\Scripts\
     ```
   - **확인** → **확인** → **확인**
   - **새 터미널 열기** 또는 **컴퓨터 재시작**

   **방법 2: 명령 프롬프트에서 확인**
   ```cmd
   # Python 설치 위치 찾기
   where python
   where py
   
   # 현재 PATH 확인
   echo %PATH%
   ```

#### 2. "command not found: make"

**macOS:** `brew install make` 또는 `xcode-select --install`

**Windows:** 반드시 Git Bash 사용 (PowerShell/CMD 아님)
- PyCharm에서 Git Bash 설정: File → Settings → Tools → Terminal → Shell path: `C:\Program Files\Git\bin\bash.exe`

#### 3. PyCharm 문제들

| 문제 | 해결법 |
|------|--------|
| Terminal 탭 없음 | View → Tool Windows → Terminal |
| make 명령어 인식 안됨 | Git Bash로 터미널 변경 |
| 가상환경 인식 안됨 | File → Settings → Project → Python Interpreter에서 venv 선택 |
| Clone 실패 | 인터넷 연결, GitHub 접근 권한 확인 |

#### 4. 서버 실행 문제들

**"Port 8000 is already in use":**
```bash
# macOS
lsof -i :8000
kill -9 <PID>

# Windows (Git Bash)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 또는 다른 포트 사용
uvicorn app.main:app --port 8001
```

**"ModuleNotFoundError":**
```bash
# 가상환경 재설정
make clean
make setup
```

#### 5. 브라우저 접속 문제

**"이 사이트에 연결할 수 없음":**
1. 서버가 실행 중인지 터미널에서 확인
2. 방화벽에서 8000번 포트 허용
3. `127.0.0.1:8000` 또는 `localhost:8000` 둘 다 시도

## 💡 자주 묻는 질문

**Q: `make setup`을 여러 번 실행해도 되나요?**
A: 네, 문제없습니다. 이미 설치된 패키지는 건너뛰고 필요한 것만 설치합니다.

**Q: PyCharm 터미널 vs 외부 터미널 차이는?**
A: PyCharm 터미널은 자동으로 프로젝트 경로와 가상환경을 설정해주어 더 편리합니다.

**Q: Windows에서 왜 Git Bash를 써야 하나요?**
A: Windows의 기본 터미널(PowerShell/CMD)은 `make` 명령어를 지원하지 않습니다. Git Bash는 Unix 명령어를 지원합니다.

**Q: Python 설치 시 "Add Python to PATH"를 체크하지 않았어요.**
A: Windows 키 + R → `sysdm.cpl` → 고급 → 환경 변수 → Path 편집에서 Python 경로를 수동으로 추가하세요. 또는 Python을 재설치할 때 "Add Python to PATH"를 체크하세요.

**Q: 서버가 실행 중일 때 다른 명령어를 실행하려면?**
A: 새 터미널 창을 열고 같은 프로젝트 폴더로 이동해서 실행하세요.

**Q: localhost가 뭔가요?**
A: `localhost`는 "내 컴퓨터"를 의미합니다. `127.0.0.1:8000`과 같은 의미로, 내 컴퓨터에서만 접속 가능한 개발용 주소입니다.

## 🔧 주요 명령어

| 명령어 | 설명 | 실행 시점 |
|--------|------|-----------|
| `make setup` | 가상환경 생성 및 의존성 설치 | 최초 1회 또는 의존성 변경 시 |
| `make local` | 로컬 서버 실행 | 개발할 때마다 |
| `make test` | API 테스트 실행 | 서버 실행 중일 때 (새 터미널에서) |
| `make clean` | 가상환경 삭제 | 문제 발생 시 재설정용 |
| `Ctrl+C` | 서버 종료 | 서버 중단하고 싶을 때 |

## 📚 추가 정보

### Python 버전 요구사항
- ✅ **사용 가능**: Python 3.11.0 ~ 3.11.8 (모든 3.11.x 버전)
- ❌ **사용 불가**: Python 3.12, 3.13, 3.10 이하 버전
- 📥 **다운로드**: [Python 3.11.8 (최신 3.11 버전)](https://www.python.org/downloads/release/python-3118/)

### 웹 브라우저에서 확인할 수 있는 페이지들
서버 실행 후 다음 주소들로 접속 가능:
- **메인 페이지**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **대체 API 문서 (ReDoc)**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

---

## 🚀 개발 진행 가이드

### 프로젝트 구조 이해

```
green-shipping-ai-server/
├── app/                    # 메인 애플리케이션 코드
│   ├── api/v1/endpoints/  # API 엔드포인트
│   ├── models/            # 데이터베이스 모델
│   ├── schemas/           # API 스키마
│   ├── main.py            # FastAPI 진입점
│   └── database.py        # 데이터베이스 연결
├── requirements.txt        # Python 의존성
└── Makefile              # 개발 명령어
```

### 환경별 실행

| 환경 | 명령어 | 데이터베이스 | 용도 |
|------|--------|-------------|------|
| **로컬 개발** | `make local` | SQLite | 개인 개발 |
| **개발 서버** | `make dev` | MySQL | 팀 개발 |
| **프로덕션** | `make prod` | MySQL | 실제 서비스 |

### 새로운 기능 개발 절차

1. **모델 정의**: `app/models/` - 데이터베이스 테이블
2. **스키마 정의**: `app/schemas/` - API 요청/응답 형식
3. **엔드포인트 생성**: `app/api/v1/endpoints/` - API 로직
4. **라우터 등록**: `app/api/v1/api.py` - 엔드포인트 연결
5. **마이그레이션**: `make migrate-create` - 데이터베이스 변경
6. **테스트**: `make test` - 기능 검증

### 유용한 개발 명령어

```bash
# 데이터베이스 마이그레이션
make migrate                              # 로컬 마이그레이션 적용
make migrate-create MESSAGE='설명'        # 새 마이그레이션 생성

# 환경별 실행
make local    # 로컬 개발 (SQLite)
make dev      # 개발 서버 (MySQL)
make prod     # 프로덕션 (MySQL)

# 기타 유틸리티
make clean    # 가상환경 삭제
make help     # 사용 가능한 명령어 확인
```

## 🤖 AI 기능(내부 전용)

본 프로젝트에는 내부 전용 생성형 AI API가 포함됩니다. 보안을 위해 반드시 헤더 토큰이 필요합니다.

- 환경변수 설정(.env):
  - `INTERNAL_API_TOKEN=your-internal-token`
  - `OPENAI_API_KEY=sk-...`
  - `AI_MODEL=gpt-5` (기본값), `EMBEDDING_MODEL=text-embedding-3-small`

- 공통: 모든 AI 엔드포인트는 요청 헤더 `X-Internal-Token: <INTERNAL_API_TOKEN>` 필요

- 채팅 질의응답
  - `POST /api/v1/ai/chat`
  - 예시:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/ai/chat \
      -H 'Content-Type: application/json' \
      -H 'X-Internal-Token: YOUR_TOKEN' \
      -d '{
        "message":"속도를 1노트 줄이면 CO2 얼마나 감소?",
        "distance_nm": 1200,
        "base_speed_knots": 14,
        "new_speed_knots": 13,
        "sfoc_g_per_kwh": 180,
        "k": 0.65,
        "language": "ko"
      }'
    ```

- 보고서 생성(PDF)
  - `POST /api/v1/ai/report`
  - 예시:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/ai/report \
      -H 'Content-Type: application/json' \
      -H 'X-Internal-Token: YOUR_TOKEN' \
      -d '{
        "title":"ESG Sample",
        "language":"ko",
        "scenarios":[
          {"distance_nm":1000, "base_speed_knots":14, "new_speed_knots":12, "sfoc_g_per_kwh":180, "k":0.65}
        ]
      }'
    ```
  - 응답: `{ "report_path": "reports/ESG-...pdf", "summary": "..." }`

- KB 인제스트/검색(관리자용)
  - `POST /api/v1/ai/kb/ingest` → `kb/` 폴더 내 PDF/MD/TXT를 벡터DB에 적재
  - `GET  /api/v1/ai/kb/search?query=...` → 상위 문서를 확인

보안 유의사항:
- 내부 토큰 미설정 시 403 반환. 토큰은 안전하게 배포/회수하세요.
- 외부 공개 금지(방화벽/Ingress 정책으로 내부망 한정 권장).
- LLM 비용/사용량 모니터링 권장.

## 🆘 도움이 필요하시다면

1. **에러 메시지를 복사해서 검색해보세요**
2. **단계별로 다시 확인해보세요**
3. **터미널 메시지를 주의깊게 읽어보세요**
4. **문제가 계속되면 `make clean` 후 `make setup`으로 재설정해보세요**

---

🎉 **설정 완료!** 이제 FastAPI 개발을 시작하세요!
=======
# GreenShipping 최단거리 초기모델 🚢
develop
